import json
import os
from pathlib import Path
import httpx
import pytest
from wger_strava.api import Strava, UnknownWrite
from wger_strava.config import Config
from wger_strava.engine import Engine
from wger_strava.state import State

pytestmark = pytest.mark.integration


@pytest.fixture
def live(tmp_path):
    path = os.environ.get("TEST_CREDENTIALS_FILE")
    if not path or not Path(path).is_file():
        pytest.skip("Run python test_harness.py for the Docker integration suite")
    fixture = json.loads(Path(path).read_text())
    config = Config(tmp_path, os.environ["WGER_BASE_URL"], fixture["token"], "mock-client", "mock-secret",
                    os.environ["STRAVA_BASE_URL"], timezone="America/Edmonton", since="2026-01-01")
    httpx.post(config.strava_url + "/__reset", trust_env=False).raise_for_status()
    state = State(tmp_path)
    state.set("mappings", fixture["mappings"])
    strava = Strava(config, state)
    strava.authorize("mock-code", "read,activity:write,activity:read_all")
    engine = Engine(config, state, strava=strava)
    yield config, state, engine, fixture
    engine.close()
    state.close()


def remote(config):
    return httpx.get(config.strava_url + "/__state", trust_env=False).json()


def test_completed_sessions_upload_native_exercises_and_survive_restart(live):
    config, state, engine, fixture = live
    preview = engine.preview()
    assert len(preview) == 2  # Unfinished and future sessions excluded.
    assert all(p["state"] == "ready" for p in preview)
    assert engine.sync()["submitted"] == 2
    assert all(p["state"] == "processing" for p in state.exports().values())
    engine.close()
    state.close()
    # New process: disk journal, persisted OAuth tokens, and async status polling.
    restarted = State(config.data_dir)
    again = Engine(config, restarted)
    try:
        assert again.sync()["submitted"] == 0
        assert {x["state"] for x in restarted.exports().values()} == {"exported"}
        assert again.sync()["submitted"] == 0
        records = remote(config)
        assert len(records["uploads"]) == len(records["requests"]) == 2
        first = records["uploads"]["1"]["payload"]
        assert first["elapsed_time"] == 2700 and first["utc_offset"] == -25200
        assert [s["exercise_type"] for s in first["sets"]] == ["BARBELL_BENCH_PRESS"] * 3 + ["PLANK_GENERIC"]
        assert first["sets"][0]["weight"] == pytest.approx(61.23497, abs=0.00001)
        assert first["sets"][3]["duration"] == 90 and "weight" not in first["sets"][3]
        assert "Synthetic wger workout" in records["uploads"]["1"]["description"]
    finally:
        again.close()
        restarted.close()


class LoseReply(httpx.BaseTransport):
    def __init__(self):
        self.inner = httpx.HTTPTransport()

    def handle_request(self, request):
        response = self.inner.handle_request(request)
        if request.method == "POST" and request.url.path == "/api/v3/uploads":
            response.read()
            response.close()
            raise httpx.ReadTimeout("Simulated lost response after commit", request=request)
        return response

    def close(self):
        self.inner.close()


@pytest.mark.parametrize("recovery", ["upload", "activity"])
def test_lost_upload_reply_holds_session_and_reconciles(live, recovery):
    config, state, engine, fixture = live
    config.batch = 1
    engine.strava.close()
    engine.strava = Strava(config, state, transport=LoseReply())
    with pytest.raises(UnknownWrite):
        engine.sync()
    assert len(remote(config)["uploads"]) == 1
    unresolved = next(iter(state.exports()))
    assert state.export(unresolved)["state"] == "uncertain"
    engine.strava.close()
    engine.strava = Strava(config, state)
    # Same session remains held on another cycle. Other completed sessions may export.
    engine.sync()
    assert len(remote(config)["uploads"]) == 2
    if recovery == "upload":
        with pytest.raises(ValueError, match="does not belong"):
            engine.reconcile(unresolved, 2)
        engine.reconcile(unresolved, 1)
    else:
        with pytest.raises(ValueError, match="does not belong"):
            engine.reconcile_activity(unresolved, 900002)
        engine.reconcile_activity(unresolved, 900001)
    engine.sync()
    assert len(remote(config)["uploads"]) == 2
    assert state.export(unresolved)["state"] == "exported"


def test_unmapped_workout_is_held_and_rotated_token_is_persisted(live):
    config, state, engine, fixture = live
    mappings = state.get("mappings")
    state.set("mappings", {})
    result = engine.sync()
    assert result["submitted"] == 0 and len(result["blocked"]) == 2
    assert not remote(config)["uploads"]
    token = state.get("oauth")
    token["expires_at"] = 0
    state.set("oauth", token)
    engine.check()
    assert state.get("oauth")["refresh_token"] == "mock-refresh-1"
    token = state.get("oauth")
    token["expires_at"] = 0
    state.set("oauth", token)
    engine.check()
    assert state.get("oauth")["refresh_token"] == "mock-refresh-2"
    state.set("mappings", mappings)
    assert engine.sync()["submitted"] == 2


def test_source_edits_are_reported_without_duplicate_or_update(live):
    config, state, engine, fixture = live
    engine.sync()
    engine.sync()
    session = fixture["sessions"][0]
    original = engine.wger.request("GET", f"/api/v2/workoutsession/{session}/")
    try:
        engine.wger.request("PATCH", f"/api/v2/workoutsession/{session}/", json={"notes": "An edit after export"})
        result = engine.sync()
        assert result["submitted"] == 0 and session in result["changed"]
        assert len(remote(config)["uploads"]) == 2
    finally:
        engine.wger.request("PATCH", f"/api/v2/workoutsession/{session}/", json={"notes": original["notes"]})
