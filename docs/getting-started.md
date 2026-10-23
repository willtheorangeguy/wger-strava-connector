# Getting started

## Prerequisites

Use Docker with Compose v2, a reachable wger 2.8.0-dev.1 API and a legacy Token API key. Register your own Strava application with callback domain `localhost`. Check Docker with `docker compose version`.

## Install

This guide covers the current source version `0.3.0`. On 2026-10-22, the latest published release was `v0.2.1`; a `v0.3.0` release download was not available. Build the checkout to use the current automatic image worker and recovery behavior.

```sh
git clone https://github.com/willtheorangeguy/wger-strava-connector.git
cd wger-strava-connector
cp .env.example .env
```

Fill in `WGER_BASE_URL` (origin reachable from the container), `WGER_TOKEN`, `STRAVA_CLIENT_ID`, `STRAVA_CLIENT_SECRET` and `WORKOUT_TIMEZONE`. The source API default is `http://host.docker.internal:8101`. Set `EXPORT_SINCE=2026-01-01` for historical backfill; an empty value saves today's UTC date on the first preview/sync as a UTC-midnight boundary.

```sh
docker compose -f compose.build.yaml build
docker compose -f compose.build.yaml run --rm connector auth-url
```

## First run

1. Open the printed Strava consent URL. Grant `read`, `activity:write`, and `activity:read_all`.
2. The browser redirects to a localhost callback and displays an expected connection error. Copy the full address from its address bar. No callback server or public connector port is required.
3. Complete authorization within 15 minutes, using the same state volume:

   ```sh
   docker compose -f compose.build.yaml run --rm -i connector auth-complete
   ```

   Paste the full callback URL at the prompt. It contains a temporary authorization code, so keep it private. Success returns `authorized_athlete` and stores rotating tokens in the journal.

4. Check the bound accounts and inspect source selection:

   ```sh
   docker compose -f compose.build.yaml run --rm connector check
   docker compose -f compose.build.yaml run --rm connector preview
   ```

   `check` returns source identity and athlete ID. `preview` reports session keys, state, missing mappings and problems without uploading activities.

5. Approve each missing exercise ID with a supported identifier before exporting.

   ```sh
   docker compose -f compose.build.yaml run --rm connector exercises
   docker compose -f compose.build.yaml run --rm connector map 123 BARBELL_BENCH_PRESS
   docker compose -f compose.build.yaml run --rm connector preview
   ```

   Replace the example ID with an actual source exercise ID from preview. Unmapped/invalid completed sets hold the whole workout.

6. Export once, then start continuous synchronization:

   ```sh
   docker compose -f compose.build.yaml run --rm connector sync
   docker compose -f compose.build.yaml up -d
   docker compose -f compose.build.yaml logs -f connector
   ```

   A successful submission commonly reports `processing` until a later sync polls the activity ID. The watcher checks immediately, then every 900 seconds by default, with a 300-second settling delay and at most ten new uploads per cycle. Unfinished/future data remains excluded. Temporary API failures are logged for a later cycle; uncertain writes stay held for explicit recovery.

## What just happened

The connector bound one wger account, Strava application and athlete to a persistent journal. It exported completed timestamped sessions with session-linked logs without modifying wger. Source edits report changed rather than updating an existing activity.

Stop the watcher before stateful one-off maintenance and restart it afterwards. Keep state: it contains tokens, account bindings, mappings, boundary and upload history. Deleting it can duplicate exports. Imported Hevy workouts are eligible; select one Strava export path to avoid cross-app duplicates.

## Next steps

- [Installation](installation.md) explains released versions and local builds.
- [Usage](usage.md) covers selection, data fidelity and recovery.
- [Configuration](configuration.md) lists defaults and overlay variables.
- [Workout images](media.md) explains the companion browser login and durable receipts.
