from datetime import datetime, timedelta, timezone
import hashlib
import time
from .api import APIError, UnknownWrite, Wger, Strava
from .state import encode
from .media.queue import enqueue, snapshot
from .media.summary import formatted_volume
from .media.muscles import collect
from .workout import build, fingerprint, stamp


class Engine:
    def __init__(self, config, state, wger=None, strava=None):
        self.config, self.state = config, state
        self.wger = wger or Wger(config)
        self.strava = strava or Strava(config, state)

    def close(self):
        self.wger.close()
        self.strava.close()

    def source(self):
        profile = self.wger.request("GET", "/api/v2/userprofile/")
        if not profile.get("username"):
            raise ValueError("wger did not return the authenticated username")
        identity = {"url": self.config.wger_url, "user": profile["username"]}
        self.state.bind("wger_account", identity)
        return identity

    def preview(self):
        identity = self.source()
        since = self.config.since or self.state.get("export_since") or datetime.now(timezone.utc).date().isoformat()
        self.state.set("export_since", since)
        rep_units = {str(x["id"]): x for x in self.wger.items("setting-repetitionunit")}
        weight_units = {str(x["id"]): x for x in self.wger.items("setting-weightunit")}
        mappings = self.state.get("mappings", {})
        cutoff = datetime.now(timezone.utc) - timedelta(seconds=self.config.settle)
        output = []
        for session in self.wger.items("workoutsession", datetime_start__gte=since + "T00:00:00Z"):
            if not session.get("datetime_end"):
                continue
            if stamp(session["datetime_end"]) > cutoff:
                continue
            logs = list(self.wger.items("workoutlog", session=session["id"]))
            try:
                payload, missing, problems = build(session, logs, mappings, rep_units, weight_units, self.config.timezone)
            except (ValueError, KeyError):
                payload, missing, problems = {}, [], ["Invalid session or set data; inspect this workout in wger"]
            day = session.get("day")
            name = "wger strength workout"
            if day:
                detail = self.wger.request("GET", f"/api/v2/day/{day}/")
                name = detail.get("name") or name
            # Include notes and title in the fingerprint so post-export edits are visible.
            content = {"payload": payload, "name": name, "notes": session.get("notes") or ""}
            current = fingerprint(content)
            previous = self.state.export(session["id"])
            state = "blocked" if missing or problems else "ready"
            if previous and previous["state"] != "retry":
                state = previous["state"]
                if state == "exported" and previous["fingerprint"] != current:
                    state = "changed"
            key = hashlib.sha256(encode(identity).encode()).hexdigest()[:16]
            external_id = f"wger-{key}-{session['id']}"
            if previous and previous["state"] == "retry":
                external_id += f".retry{previous['attempt']}"
            external_id += ".json"
            if previous and previous["state"] != "retry":
                external_id = previous["external_id"]
            output.append({"session": str(session["id"]), "state": state, "missing": missing, "problems": problems,
                           "exercise_ids": sorted({str(log["exercise"]) for log in logs}),
                           "fingerprint": current, "external_id": external_id, **content})
        return output

    def media_snapshot(self, plan):
        details, unavailable = [], []
        cache = getattr(self, '_muscle_cache', {})
        self._muscle_cache = cache
        for exercise in plan.get('exercise_ids', []):
            # Source IDs are numeric; never interpolate arbitrary source text into a URL.
            if not exercise.isdigit():
                unavailable.append(exercise)
                continue
            try:
                if exercise not in cache:
                    cache[exercise] = self.wger.request('GET', '/api/v2/exerciseinfo/' + exercise + '/')
                details.append(cache[exercise])
            except (APIError, ValueError):
                # Optional artwork metadata must not prevent an otherwise valid export.
                unavailable.append(exercise)
        result = snapshot({**plan, 'muscles': collect(details, 'muscles', 'muscles_secondary')}, self.config)
        result['unavailable_exercises'] = unavailable
        return result

    def check(self):
        identity = self.source()
        athlete = self.strava.call("GET", "/athlete")
        self.state.bind("strava_athlete", str(athlete["id"]))
        return {"wger": identity, "strava_athlete": str(athlete["id"])}

    def finish(self, session, record, upload):
        if str(upload.get("external_id")) != record["external_id"]:
            raise ValueError("Strava upload external ID does not match this session")
        if upload.get("error"):
            record["state"] = "failed"
            # Never persist untrusted HTML error messages from Strava.
            record["reason"] = "Strava rejected the upload; inspect the upload on Strava"
        elif upload.get("activity_id"):
            record["state"] = "exported"
            record["activity_id"] = str(upload["activity_id"])
        else:
            record["state"] = "processing"
        self.state.save(session, record)
        self.queue_media(session, record)

    def queue_media(self, session, record):
        try:
            enqueue(self.config, self.state, record)
            record.pop("media_error", None)
        except (OSError, ValueError):
            record["media_error"] = "Image queue unavailable; workout remains exported"
        self.state.save(session, record)

    def sync(self):
        if self.state.get("cooldown", 0) > time.time():
            return {"state": "rate_limited", "retry_at": self.state.get("cooldown")}
        self.check()
        self._muscle_cache = {}
        # Poll previous jobs first, even if their source was subsequently edited/deleted.
        for session, record in self.state.exports().items():
            if record["state"] == "processing":
                upload = self.strava.call("GET", "/uploads/" + record["upload_id"])
                self.finish(session, record, upload)
        for session, record in self.state.exports().items():
            if record["state"] == "exported" and record.get("media"):
                self.queue_media(session, record)
        plans = self.preview()
        submitted = 0
        for plan in plans:
            if plan["state"] != "ready" or submitted >= self.config.batch:
                continue
            record = {key: plan[key] for key in ("fingerprint", "external_id")}
            previous = self.state.export(plan["session"])
            if previous:
                record.update({key: previous[key] for key in ("attempt", "attempts") if key in previous})
            if self.config.media_enabled:
                record["media"] = self.media_snapshot(plan)
            record["state"] = "uncertain"
            # Commit intent before the POST: a crash or lost reply must not cause another upload.
            self.state.save(plan["session"], record)
            try:
                upload = self.strava.call("POST", "/uploads", data={
                    "data_type": "json", "sport_type": "WeightTraining", "trainer": "1",
                    "name": plan["name"], "description": ("Exported from wger.\n" + plan["notes"] + "\nTotal weight lifted: " + formatted_volume(plan["payload"]["sets"], self.config.media_units) + " " + self.config.media_units + " (external load x repetitions).")[:10000],
                    "external_id": plan["external_id"]},
                    files={"file": (plan["external_id"], encode(plan["payload"]).encode(), "application/json")})
                if not isinstance(upload, dict) or not (upload.get("id_str") or upload.get("id")):
                    raise UnknownWrite("POST", "/api/v3/uploads")
                record["upload_id"] = str(upload.get("id_str") or upload["id"])
                # Save ID before interpreting the remainder, so restart can poll it.
                record["state"] = "processing"
                self.state.save(plan["session"], record)
                self.finish(plan["session"], record, upload)
                submitted += 1
            except UnknownWrite:
                # Remains uncertain; no automatic POST retry even across process restarts.
                raise
            except APIError as error:
                if error.status == 429 or error.status == 401:
                    # Explicit rejection, not an ambiguous transport failure.
                    self.state.db.execute("DELETE FROM exports WHERE session=?", (plan["session"],))
                    self.state.db.commit()
                else:
                    record["state"] = "failed"
                    record["reason"] = str(error)
                    self.state.save(plan["session"], record)
                raise
        return {"submitted": submitted, "exports": self.state.exports(),
                "blocked": [{k: p[k] for k in ("session", "missing", "problems")} for p in plans if p["state"] == "blocked"],
                "changed": [p["session"] for p in plans if p["state"] == "changed"]}

    def retry(self, session):
        record = self.state.export(session)
        if not record or record["state"] not in {"uncertain", "failed"}:
            raise ValueError("Only uncertain or failed uploads can be retried")
        self.check()
        if record.get("upload_id"):
            upload = self.strava.call("GET", "/uploads/" + record["upload_id"])
            if str(upload.get("external_id")) != record["external_id"]:
                raise ValueError("Strava upload external ID does not match this session")
            if upload.get("activity_id") or not upload.get("error"):
                raise ValueError("Prior upload is successful or processing; reconcile it instead of retrying")
        # Keep the session identity and journal; only an explicit retry gets a
        # fresh file ID, avoiding Strava's cache of previously failed uploads.
        attempts = record.get("attempts", []) + [{key: record[key] for key in
                    ("external_id", "upload_id", "state", "reason") if key in record}]
        record["attempt"] = record.get("attempt", len(record.get("attempts", []))) + 1
        record["attempts"] = attempts
        record["state"] = "retry"
        self.state.save(session, record)
        return {"retry_allowed": session, "attempt": record["attempt"]}

    def reconcile(self, session, upload_id):
        self.check()
        record = self.state.export(session)
        if not record or record["state"] not in {"uncertain", "processing", "failed"}:
            raise ValueError("Session must have an unresolved upload")
        upload = self.strava.call("GET", "/uploads/" + str(int(upload_id)))
        if upload.get("external_id") != record["external_id"]:
            raise ValueError("Upload does not belong to this wger session")
        record["upload_id"] = str(upload.get("id_str") or upload["id"])
        self.finish(session, record, upload)
        return self.state.export(session)

    def reconcile_activity(self, session, activity_id):
        self.check()
        record = self.state.export(session)
        if not record or record["state"] not in {"uncertain", "processing", "failed"}:
            raise ValueError("Session must have an unresolved upload")
        activity = self.strava.call("GET", "/activities/" + str(int(activity_id)))
        if activity.get("external_id") != record["external_id"]:
            raise ValueError("Activity does not belong to this wger session")
        record.update(state="exported", activity_id=str(activity["id"]))
        self.state.save(session, record)
        self.queue_media(session, record)
        return record
