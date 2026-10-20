"""Translate actual sets, never prescribed targets, into Strava strength JSON."""
from datetime import datetime
from decimal import Decimal, InvalidOperation
import hashlib
from importlib.resources import files
import json
from zoneinfo import ZoneInfo
from .state import encode


EXERCISES = frozenset(json.loads(files("wger_strava").joinpath("exercises.json").read_text(encoding="utf-8")))


def stamp(value):
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("Workout timestamps must include a timezone")
    return result


def numeric(value, *, integer=False):
    try:
        number = Decimal(str(value))
    except InvalidOperation:
        raise ValueError("Invalid logged number") from None
    if not number.is_finite() or number < 0:
        raise ValueError("Logged numbers must be finite and nonnegative")
    if integer and number != number.to_integral_value():
        raise ValueError("Strava requires whole repetitions or seconds")
    return int(number) if integer else float(number)


def build(session, logs, mappings, rep_units, weight_units, timezone):
    start, end = stamp(session["datetime_start"]), stamp(session["datetime_end"])
    seconds = (end - start).total_seconds()
    if seconds < 1 or seconds != int(seconds):
        # wger stores fractional timestamps; round session duration, not reps.
        if seconds < 1:
            raise ValueError("Workout duration must be positive")
    local = start.astimezone(ZoneInfo(timezone))
    sets, missing, problems = [], set(), []
    ordered = sorted(logs, key=lambda row: (stamp(row["date"]), str(row["id"])))
    for log in ordered:
        exercise = str(log["exercise"])
        target = mappings.get(exercise)
        if target is None:
            missing.add(exercise)
            continue
        if target not in EXERCISES:
            problems.append(f"Exercise {exercise}: unknown Strava exercise identifier")
            continue
        item = {"exercise_type": target}
        try:
            if str(log.get("session")) != str(session["id"]):
                raise ValueError("Set belongs to another session")
            if log.get("repetitions") is None:
                raise ValueError("Set has no actual repetitions or duration")
            unit = rep_units[str(log["repetitions_unit"])]
            kind = unit.get("unit_type")
            if kind == "REPETITIONS":
                item["repetitions"] = numeric(log["repetitions"], integer=True)
            elif kind == "TIME":
                item["duration"] = numeric(Decimal(str(log["repetitions"])) * Decimal(str(unit["multiplier"])), integer=True)
            else:
                raise ValueError("Distance sets cannot be represented as strength sets")
            if not item.get("repetitions", item.get("duration", 0)):
                raise ValueError("Set has zero actual repetitions or duration")
            weight_unit = weight_units.get(str(log.get("weight_unit")), {}).get("name", "").casefold()
            if log.get("weight") is not None:
                load = numeric(log["weight"])
                if weight_unit == "kg":
                    item["weight"] = load
                elif weight_unit in {"lb", "lbs"}:
                    item["weight"] = round(load * 0.45359237, 6)
                elif weight_unit != "body weight":
                    raise ValueError("Unsupported load unit; plates and speed are not kilograms")
            when = stamp(log["date"])
            if start <= when <= end:
                item["start_time"] = when.isoformat()
            sets.append(item)
        except (ValueError, KeyError, InvalidOperation) as error:
            problems.append(f"Set {log['id']}: {error}")
    if not logs:
        problems.append("No completed sets attached to this session")
    payload = {"version": "1.0", "start_time": start.isoformat(), "utc_offset": int(local.utcoffset().total_seconds()),
               "elapsed_time": int(round(seconds)), "creator": {"name": "wger-strava-connector"}, "sets": sets}
    return payload, sorted(missing), problems


def fingerprint(payload):
    return hashlib.sha256(encode(payload).encode()).hexdigest()
