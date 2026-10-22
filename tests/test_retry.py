"""Regression coverage for explicitly retrying a cached failed Strava upload."""
import pytest

from wger_strava.config import Config
from wger_strava.engine import Engine
from wger_strava.state import State
from test_watch import Source


class Destination:
    def __init__(self, external_id):
        self.prior = {"external_id": external_id, "error": "Error Processing Data", "activity_id": None}
        self.uploads = []

    def call(self, method, path, **kwargs):
        if path == "/athlete":
            return {"id": 123}
        if path == "/uploads/7":
            return self.prior
        assert method == "POST" and path == "/uploads"
        self.uploads.append(kwargs)
        return {"id": 8, "external_id": kwargs["data"]["external_id"], "activity_id": 999}

    def close(self):
        pass


def setup_engine(tmp_path):
    source = Source(True)
    source.complete = True
    state = State(tmp_path)
    state.set("mappings", {source.exercise_id: "BARBELL_BENCH_PRESS"})
    config = Config(tmp_path, "https://source.test", "key", "client", "secret", since=source.day)
    engine = Engine(config, state, source)
    plan = engine.preview()[0]
    engine.strava.close()
    destination = Destination(plan["external_id"])
    engine.strava = destination
    record = {"fingerprint": plan["fingerprint"], "external_id": plan["external_id"],
              "state": "failed", "upload_id": "7", "reason": "Strava rejected the upload"}
    state.save(plan["session"], record)
    return engine, plan, record


def test_retry_uses_fresh_identifier_and_retains_history_across_restart(tmp_path):
    engine, plan, original = setup_engine(tmp_path)
    config, source, destination = engine.config, engine.wger, engine.strava
    try:
        assert engine.retry(plan["session"])["attempt"] == 1
        queued = engine.preview()[0]
        assert queued["state"] == "ready"
        assert queued["external_id"] == plan["external_id"].removesuffix(".json") + ".retry1.json"
    finally:
        engine.close()
        engine.state.close()
    state = State(tmp_path)
    engine = Engine(config, state, source, destination)
    try:
        assert engine.preview()[0]["external_id"] == queued["external_id"]
        assert engine.sync()["submitted"] == 1
        exported = state.export(plan["session"])
        assert exported["state"] == "exported" and exported["attempt"] == 1
        assert exported["attempts"] == [{k: original[k] for k in ("external_id", "upload_id", "state", "reason")}]
        assert engine.sync()["submitted"] == 0 and len(destination.uploads) == 1
    finally:
        engine.close()
        state.close()


@pytest.mark.parametrize("error,activity_id", [(None, None), (None, 999), ("stale error", 999)])
def test_retry_refuses_remote_success_and_in_progress_jobs(tmp_path, error, activity_id):
    engine, plan, original = setup_engine(tmp_path)
    engine.strava.prior.update(error=error, activity_id=activity_id)
    try:
        with pytest.raises(ValueError, match="reconcile"):
            engine.retry(plan["session"])
        assert engine.state.export(plan["session"]) == original
    finally:
        engine.close()
        engine.state.close()


def test_retry_revalidates_current_source_and_mappings(tmp_path):
    engine, plan, _ = setup_engine(tmp_path)
    try:
        engine.retry(plan["session"])
        engine.state.set("mappings", {})
        assert engine.preview()[0]["state"] == "blocked"
        assert engine.sync()["submitted"] == 0 and engine.strava.uploads == []
    finally:
        engine.close()
        engine.state.close()
