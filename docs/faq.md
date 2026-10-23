# FAQ

???+ question "Does it change my wger workouts?"

    No. The connector reads wger and creates Strava activities. Its journal is local.

??? question "Will Hevy imports be exported twice?"

    Imported wger sessions are eligible. If Hevy also sends workouts directly to Strava, select one export path. This connector's journal does not deduplicate writes made by another app.

??? question "Do I need to run sync after every workout?"

    No. `docker compose -f compose.build.yaml up -d` starts the watcher. With defaults, completed sessions become eligible after five minutes and are discovered on a subsequent 15-minute cycle.

??? question "Does preview leave all local state untouched?"

    No. It never uploads an activity, but it binds the source identity and persists the initial date boundary. Set `EXPORT_SINCE=2026-01-01` explicitly when you intend to backfill.

??? question "Why do cards need a second Strava login?"

    API OAuth handles workouts. Chromium uses a separate saved browser session for photo attachment. Both must identify the same athlete.

??? question "Are existing exports updated when I edit wger?"

    No. Changed fingerprints are reported as `changed`. This version does not update/delete existing Strava activities or backfill old image jobs automatically.
