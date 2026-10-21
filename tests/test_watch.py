"""Exercise the persistent CLI watcher through a real synchronization engine."""
from datetime import datetime, timedelta, timezone

import pytest

from wger_strava import cli
from wger_strava.api import APIError
from wger_strava.config import Config
from wger_strava.engine import Engine
from wger_strava.state import State


class Source:
    exercise_id = "1"

    def __init__(self, up):
        self.up, self.complete, self.closed = up, False, False
        self.day = (datetime.now(timezone.utc) - timedelta(days=2)).date().isoformat()

    def request(self, method, path):
        if not self.up:
            raise APIError(method, path)
        assert method == "GET" and path == "/api/v2/userprofile/"
        return {"username": "watch-test"}

    def items(self, route, **filters):
        if route == "setting-repetitionunit":
            return [{"id": 1, "unit_type": "REPETITIONS", "multiplier": 1}]
        if route == "setting-weightunit":
            return [{"id": 1, "name": "kg"}]
        if route == "workoutsession":
            return [{"id": "session", "datetime_start": self.day + "T10:00:00Z",
                     "datetime_end": self.day + "T11:00:00Z" if self.complete else None}]
        assert route == "workoutlog"
        return [{"id": "set", "session": "session", "date": self.day + "T10:05:00Z",
                 "exercise": 1, "repetitions": 8, "repetitions_unit": 1,
                 "weight": 100, "weight_unit": 1}]

    def close(self):
        self.closed = True


class Destination:
    def __init__(self):
        self.uploads, self.polls, self.closed = [], 0, False

    def call(self, method, path, **kwargs):
        if path == "/athlete":
            return {"id": 123}
        if method == "POST":
            assert path == "/uploads"
            self.uploads.append(kwargs)
            return {"id": 7, "external_id": kwargs["data"]["external_id"], "activity_id": None}
        assert path == "/uploads/7"
        self.polls += 1
        return {"id": 7, "external_id": self.uploads[0]["data"]["external_id"], "activity_id": 99}

    def close(self):
        self.closed = True


@pytest.mark.parametrize("initial_outage", [False, True])
def test_watch_detects_later_completion_and_exports_once_without_manual_sync(tmp_path, monkeypatch, capsys, initial_outage):
    source, destination = Source(not initial_outage), Destination()
    config = Config(tmp_path, "https://source.test", "test-key", "client", "secret", since=source.day)
    state = State(tmp_path)
    state.set("mappings", {source.exercise_id: "BARBELL_BENCH_PRESS"})
    state.close()
    monkeypatch.setattr(cli.Config, "env", lambda: config)
    monkeypatch.setattr(cli, "Engine", lambda config, state: Engine(config, state, source, destination))
    monkeypatch.setattr("sys.argv", ["connector", "watch"])
    sleeps = []

    def next_cycle(seconds):
        sleeps.append(seconds)
        if len(sleeps) == 1:
            assert not destination.uploads
            source.up = True
        elif len(sleeps) == 2:
            assert not destination.uploads
            # The source workout completes after the watcher is already running.
            source.complete = True
        elif len(sleeps) == 4:
            raise KeyboardInterrupt

    monkeypatch.setattr(cli.time, "sleep", next_cycle)
    cli.main()
    assert sleeps == [900] * 4
    assert len(destination.uploads) == 1 and destination.polls == 1
    assert source.closed and destination.closed
    output = capsys.readouterr()
    assert '"submitted": 1' in output.out
    assert ("network error" in output.err) == initial_outage
    reopened = State(tmp_path)
    try:
        assert reopened.get("last_cycle")
        assert [record["state"] for record in reopened.exports().values()] == ["exported"]
    finally:
        reopened.close()
