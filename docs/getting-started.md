# Getting started

## Prerequisites

Use Docker with Compose v2 and a reachable wger `2.8.0-dev.1` API. You need its legacy API token and your own Strava application. Check Docker with `docker compose version`.

## Install

The connector is an always-running companion service to wger. After one-time
Strava authorization and exercise mapping, `docker compose up -d` starts its
`watch` loop. Keep wger and the connector running together; daily manual `sync`
commands are unnecessary. The existing-stack overlay runs the same watcher next
to wger on its Compose network, while standalone deployment reaches wger by URL.

The watcher checks immediately, then every `SYNC_INTERVAL_SECONDS` (900 seconds
by default). When a session has an end time and is at least `SETTLE_SECONDS`
(300 seconds) old, it automatically uploads the eligible workout and polls Strava
until processing finishes. With defaults, discovery normally takes 5–20 minutes
after completion. Previously exported sessions are not uploaded again.

Temporary wger/Strava API failures are logged and checked again on the next cycle.
`restart: unless-stopped` restarts the container after a process failure or Docker
restart. Keep its state volume. Missing exercise mappings still hold a workout for
review, and uncertain uploads still require reconciliation to prevent duplicates.

Create an empty directory and put these two files in it:

- `docker-compose.yml`
- `.env`: copy `.env.example` from this repository, or rename the release download `env.example` to `.env`.

No source checkout, Python installation, or local image build is needed. Download the files from [release v0.3.0](https://github.com/willtheorangeguy/wger-strava-connector/releases/tag/v0.3.0). The Compose file pulls `ghcr.io/willtheorangeguy/wger-strava-connector:0.3.0`. Each release includes all four standalone/existing-wger setup files as downloads after its container publishing workflow completes.

Fill in `.env`:

- `WGER_BASE_URL`: your wger server, reachable **from the connector container**. The example uses the local harness on port 8101.
- `WGER_TOKEN`: your wger **legacy API token** from your account settings.
- `STRAVA_CLIENT_ID` and `STRAVA_CLIENT_SECRET`: create your own application at [Strava API settings](https://www.strava.com/settings/api). Set its authorization callback domain to `localhost`.
- `WORKOUT_TIMEZONE`: your IANA timezone, for example `America/Edmonton`.
- `EXPORT_SINCE`: optional `YYYY-MM-DD` boundary at midnight UTC. Leave blank to start with today's UTC date, saved on the first preview/sync. Set a date explicitly to backfill older sessions.
- `CONNECTOR_VERSION`: the released image version, without `v`. Release downloads select their matching version automatically.

Then pull the image and authorize your Strava account once:

```sh
docker compose pull
docker compose run --rm connector auth-url
```

Open the printed URL and allow the requested permissions. Your browser will redirect to `http://localhost/strava/callback?...`. **A connection error on that page is expected:** copy the complete URL from the address bar. No callback server or public port is needed.

```sh
docker compose run --rm -i connector auth-complete
```

Paste that complete callback URL at the prompt. The URL contains a temporary authorization code: keep it private. Authorization checks the state nonce, its 15-minute expiry, and the granted scopes. Requested scopes are `read` (verify your athlete), `activity:write` (uploads), and `activity:read_all` (access to private activities for recovery/inspection). Tokens are stored in the state volume and rotated automatically; they do not belong in `.env`.

```sh
docker compose run --rm connector check
docker compose run --rm connector preview
docker compose run --rm connector exercises
docker compose run --rm connector map 123 BARBELL_BENCH_PRESS
docker compose run --rm connector map 456 PLANK_GENERIC
docker compose run --rm connector preview
docker compose run --rm connector sync
docker compose up -d
docker compose logs -f connector
```

Replace `123` and `456` with the wger exercise IDs listed as missing by `preview`. Look up their names in wger's exercise page/API (`/api/v2/exerciseinfo/<ID>/`). Choose an identifier from `exercises`; `mappings` lists your approvals. An unmapped or unsupported set holds the **whole workout**, so the activity is never silently missing exercises.

Strava processes uploads asynchronously. The first `sync` usually records `processing`; another sync or the background polling cycle records the resulting activity ID. Background sync runs every 15 minutes by default, uploading at most 10 workouts per cycle. A finished session must be at least 5 minutes old to allow recently saved sets to settle. Unfinished and future sessions are excluded.

Run **one connector per wger account and Strava athlete**. Stop the background service before running commands that open the state volume:

```sh
docker compose stop connector
docker compose run --rm connector status
# Make mappings, preview, reconcile, or authorize again here.
docker compose up -d
```

State is bound to the source username/server and destination athlete/application. Keep the state volume: it contains your tokens, mappings, date boundary, and upload journal. Deleting it can cause duplicate exports. Back it up with the service stopped. Imported Hevy workouts in wger are eligible too; if Hevy already exports them to Strava, use one export path to avoid duplicates across apps. Strava's duplicate detection does not guarantee cross-app deduplication.

## What just happened

The source account and destination athlete are bound to a persistent journal. The watcher exports completed, settled sessions and polls asynchronous Strava uploads. `preview` can write the initial date boundary but never uploads an activity.

## Next steps

- Use [configuration](configuration.md) for environment defaults and the existing-stack naming scheme.
- Read [deployment](deployment.md) before changing state volumes.
- Enable optional [workout images](media.md) after core exports work.
