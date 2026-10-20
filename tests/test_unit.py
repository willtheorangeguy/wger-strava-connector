import time
from urllib.parse import urlencode
import httpx
import pytest
from wger_strava.api import API, APIError, Strava, UnknownWrite
from wger_strava.cli import complete_callback
from wger_strava.config import Config
from wger_strava.state import State
from wger_strava.workout import EXERCISES, build


SESSION = {"id": "session1", "datetime_start": "2026-07-01T18:00:00Z", "datetime_end": "2026-07-01T19:00:00Z"}
LOG = {"id": "set1", "session": "session1", "date": "2026-07-01T18:05:00Z", "exercise": 1,
       "repetitions": "8.00", "repetitions_target": "20", "repetitions_unit": 1,
       "weight": "100", "weight_target": "200", "weight_unit": 1}
REPS = {"1": {"unit_type": "REPETITIONS", "multiplier": 1}, "2": {"unit_type": "TIME", "multiplier": 60},
        "3": {"unit_type": "DISTANCE", "multiplier": 1}}
WEIGHTS = {"1": {"name": "kg"}, "2": {"name": "lb"}, "3": {"name": "Body Weight"}, "4": {"name": "Plates"}}
MAPPINGS = {"1": "BARBELL_BENCH_PRESS"}


def translate(log=None, session=None, mappings=None):
    return build(session or SESSION, [LOG if log is None else log], MAPPINGS if mappings is None else mappings,
                 REPS, WEIGHTS, "America/Edmonton")


def test_structured_sets_use_actual_values_and_local_offset():
    payload, missing, problems = translate()
    assert not missing and not problems
    assert payload["utc_offset"] == -21600 and payload["elapsed_time"] == 3600
    assert payload["sets"] == [{"exercise_type": "BARBELL_BENCH_PRESS", "repetitions": 8,
                               "weight": 100, "start_time": "2026-07-01T18:05:00+00:00"}]
    assert "CLEAN" in EXERCISES and "BARBELL_BACK_SQUAT" in EXERCISES and len(EXERCISES) == 656


@pytest.mark.parametrize("changes,field,value", [
    ({"weight_unit": 2}, "weight", 45.359237),
    ({"weight_unit": 3}, "repetitions", 8),
    ({"repetitions_unit": 2, "repetitions": "1.5"}, "duration", 90),
])
def test_unit_conversion(changes, field, value):
    payload, missing, problems = translate({**LOG, **changes})
    assert not missing and not problems
    assert payload["sets"][0][field] == value
    if changes.get("weight_unit") == 3:
        assert "weight" not in payload["sets"][0]


@pytest.mark.parametrize("changes", [
    {"repetitions": None}, {"repetitions": "1.5"}, {"repetitions": 0}, {"repetitions": -1},
    {"weight": "NaN"}, {"weight": "Infinity"}, {"weight": -1}, {"weight_unit": 4},
    {"repetitions_unit": 3}, {"repetitions_unit": 88}, {"session": "another-session"},
])
def test_invalid_or_unrepresentable_sets_block_whole_workout(changes):
    payload, missing, problems = translate({**LOG, **changes})
    assert problems and not payload["sets"]


def test_missing_and_invalid_mapping_are_explicit():
    assert translate(mappings={})[1] == ["1"]
    assert translate(mappings={"1": "INVENTED_EXERCISE"})[2]


@pytest.mark.parametrize("changes", [
    {"datetime_start": "2026-07-01T18:00:00"}, {"datetime_end": "2026-07-01T17:00:00Z"},
])
def test_invalid_session_times(changes):
    with pytest.raises(ValueError):
        translate(session={**SESSION, **changes})


def test_state_is_durable_bound_and_exclusive(tmp_path):
    state = State(tmp_path)
    try:
        state.bind("account", {"id": 1})
        with pytest.raises(ValueError, match="Account"):
            state.bind("account", {"id": 2})
        state.save("session", {"state": "uncertain"})
        with pytest.raises(ValueError, match="Another connector"):
            State(tmp_path)
    finally:
        state.close()
    reopened = State(tmp_path)
    try:
        assert reopened.export("session") == {"state": "uncertain"}
    finally:
        reopened.close()


def test_pagination_origin_does_not_leak_auth():
    requests = []
    def handler(request):
        requests.append(request)
        return httpx.Response(200, json={})
    api = API("https://wger.test", headers={"Authorization": "Token test"}, transport=httpx.MockTransport(handler))
    try:
        with pytest.raises(ValueError):
            api.request("GET", "https://attacker.test/steal")
        assert not requests
    finally:
        api.close()


@pytest.mark.parametrize("status,error", [(400, APIError), (401, APIError), (500, UnknownWrite), (503, UnknownWrite)])
def test_post_never_retries_and_errors_do_not_include_secrets(status, error):
    requests = []
    def handler(request):
        requests.append(request)
        return httpx.Response(status, json={"secret": "private-token-value"})
    api = API("https://strava.test", transport=httpx.MockTransport(handler))
    try:
        with pytest.raises(error) as failure:
            api.request("POST", "/api/v3/uploads", json={})
        assert "private-token-value" not in str(failure.value)
        assert len(requests) == 1
    finally:
        api.close()


def test_daily_rate_limit_is_persisted_without_retrying(tmp_path):
    state = State(tmp_path)
    api = API("https://strava.test", state=state, transport=httpx.MockTransport(lambda request: httpx.Response(
        429, headers={"Retry-After": "120", "X-RateLimit-Limit": "200,2000", "X-RateLimit-Usage": "200,2000"}, json={})))
    try:
        with pytest.raises(APIError):
            api.request("POST", "/api/v3/uploads")
        assert state.get("cooldown") >= time.time() + 86400 - time.time() % 86400 - 1
    finally:
        api.close()
        state.close()


def test_oauth_callback_checks_nonce_expiry_and_consent(tmp_path):
    state = State(tmp_path)
    try:
        state.set("authorization", {"state": "good", "expires": time.time() + 60})
        good = "http://localhost/strava/callback?" + urlencode({"state": "good", "code": "code", "scope": "read,activity:write"})
        assert complete_callback(state, good) == ("code", "read,activity:write")
        with pytest.raises(ValueError, match="state"):
            complete_callback(state, good.replace("good", "wrong"))
        with pytest.raises(ValueError, match="declined"):
            complete_callback(state, "http://localhost/?state=good&error=access_denied")
        state.set("authorization", {"state": "good", "expires": 0})
        with pytest.raises(ValueError, match="expired"):
            complete_callback(state, good)
    finally:
        state.close()


def test_oauth_refresh_rotation_is_durable_and_not_repeated(tmp_path):
    config = Config(tmp_path, "https://wger.test", "token", "client", "secret", "https://strava.test")
    state = State(tmp_path)
    calls = []
    state.set("oauth", {"access_token": "old", "refresh_token": "refresh-old", "expires_at": 0})
    def handler(request):
        calls.append(request)
        assert b"refresh_token=refresh-old" in request.content
        return httpx.Response(200, json={"access_token": "new", "refresh_token": "refresh-new", "expires_at": int(time.time())+3600})
    api = Strava(config, state, transport=httpx.MockTransport(handler))
    try:
        assert api.token() == api.token() == "new"
        assert len(calls) == 1 and state.get("oauth")["refresh_token"] == "refresh-new"
        state.set("refresh_uncertain", True)
        state.set("oauth", {"access_token": "old", "refresh_token": "refresh-old", "expires_at": 0})
        with pytest.raises(ValueError, match="uncertain"):
            api.token()
    finally:
        api.close()
        state.close()


def test_refresh_lost_reply_blocks_reuse_after_restart(tmp_path):
    config = Config(tmp_path, "https://wger.test", "token", "client", "secret", "https://strava.test")
    state = State(tmp_path)
    state.set("oauth", {"access_token": "old", "refresh_token": "refresh-old", "expires_at": 0})
    def lost(request):
        raise httpx.ReadTimeout("lost", request=request)
    api = Strava(config, state, transport=httpx.MockTransport(lost))
    try:
        with pytest.raises(UnknownWrite):
            api.token()
        assert state.get("refresh_uncertain")
    finally:
        api.close()
        state.close()
    reopened = State(tmp_path)
    api = Strava(config, reopened, transport=httpx.MockTransport(lost))
    try:
        with pytest.raises(ValueError, match="uncertain"):
            api.token()
    finally:
        api.close()
        reopened.close()


@pytest.mark.parametrize("response", [{}, {"access_token": "sensitive", "refresh_token": "sensitive", "expires_at": None}])
def test_invalid_token_responses_fail_without_revealing_credentials(response):
    with pytest.raises(ValueError) as error:
        Strava.credentials(response)
    assert "sensitive" not in str(error.value)


@pytest.mark.parametrize("url", ["file:///etc/passwd", "https://token@host", "https://host?key=token"])
def test_reject_credential_bearing_or_invalid_base_urls(tmp_path, url):
    with pytest.raises(ValueError):
        Config(tmp_path, url, "token", "client", "secret")
