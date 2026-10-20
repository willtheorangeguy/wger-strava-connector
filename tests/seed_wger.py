"""Executed only inside the sibling harness, under a temporary dedicated user."""
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import json
import secrets
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework.authtoken.models import Token
from wger.exercises.models import Exercise
from wger.manager.models import Routine, Day, WorkoutSession, WorkoutLog

with transaction.atomic():
    user = User.objects.create_user(username=USERNAME, password=secrets.token_urlsafe(32))
    routine = Routine.objects.create(user=user, name="Strava export test", start="2026-01-01", end="2026-12-31")
    day = Day.objects.create(routine=routine, order=1, name="Upper + core")
    exercises = [Exercise.objects.filter(translations__name__iexact=name).distinct().order_by("pk").first()
                 for name in ("Bench Press", "Plank")]
    if any(exercise is None for exercise in exercises):
        raise ValueError("Expected Bench Press and Plank in the harness exercise catalog")
    start = datetime(2026, 1, 10, 18, tzinfo=timezone.utc)
    sessions = []
    for index in range(4):
        when = start + timedelta(days=index)
        if index == 3:
            when = datetime.now(timezone.utc) + timedelta(days=2)
        session = WorkoutSession.objects.create(user=user, routine=routine, day=day, datetime_start=when,
                    datetime_end=None if index == 2 else when + timedelta(minutes=45), notes="Synthetic wger workout")
        for set_no in range(3):
            WorkoutLog.objects.create(user=user, session=session, routine=routine, exercise=exercises[0],
                date=when+timedelta(minutes=set_no+1), repetitions=10-set_no, weight=Decimal("135.0"), weight_unit_id=2)
        WorkoutLog.objects.create(user=user, session=session, routine=routine, exercise=exercises[1],
                date=when+timedelta(minutes=10), repetitions=Decimal("1.5"), repetitions_unit_id=4,
                weight=0, weight_unit_id=3)
        sessions.append(str(session.pk))
    token = Token.objects.get_or_create(user=user)[0].key
print("CONNECTOR_TEST_JSON=" + json.dumps({"username": user.username, "token": token, "sessions": sessions,
    "mappings": {str(exercises[0].pk): "BARBELL_BENCH_PRESS", str(exercises[1].pk): "PLANK_GENERIC"}}))
