# wger → Strava connector

Export completed **wger strength workouts** to Strava, including individual exercises, sets, repetitions, weights, and timed sets. A separate Docker service reads your wger API and uploads a structured `WeightTraining` activity to Strava. It does not modify wger.

Version 0.2.0 adds experimental [workout cards and headless-browser login tools](design/README.md): dark muscle-summary cards, 30 illustrated weight comparisons, and saved browser login. Version 0.2.1 refines 19 comparison illustrations, including distinct animal profiles, detailed vehicles, landmarks, a side-view airliner, and a carrier with parked aircraft. A live test attached both sample cards to a consenting account's private activity. Automatic image generation/attachment during production workout sync remains pending.

Uses Strava's documented [strength JSON upload format](https://developers.strava.com/docs/uploads/#json---strength-training-limited), rather than putting the exercises only in an activity description. Exercise names map to Strava's supported identifiers so Strava can display the workout log and muscle map. Strava may group variants under a more general exercise.

The strength exporter is tested against the [wger addon harness](https://github.com/willtheorangeguy/wger-addon-harness), pinned to wger `2.8.0-dev.1`. It requires sessions with `datetime_start`, `datetime_end`, and logs linked by `session`. Legacy wger versions with date/time-only sessions are not supported. Automated strength-upload tests use a local API double implementing the documented contract; the separate live browser photo test does not validate strength JSON uploads against a real account.

## Docker setup

Create an empty directory and put these two files in it:

- `docker-compose.yml`
- `.env`: copy `.env.example` from this repository, or rename the release download `env.example` to `.env`.

No source checkout, Python installation, or local image build is needed. Download the files from [release v0.2.1](https://github.com/willtheorangeguy/wger-strava-connector/releases/tag/v0.2.1). The Compose file pulls `ghcr.io/willtheorangeguy/wger-strava-connector:0.2.1`. Each release includes all four standalone/existing-wger setup files as downloads after its container publishing workflow completes.

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

## Add to an existing wger Docker Compose stack

Copy [`examples/docker-compose.wger.yml`](examples/docker-compose.wger.yml) beside your existing wger Compose file, and add the settings from [`examples/wger.env.example`](examples/wger.env.example) to that stack's `.env`. These two files are also release downloads. No connector source checkout or build context is needed.

The default URL `http://web:8000` assumes your wger service is named `web` and both services use the default Compose network. If your service has another name, change `STRAVA_WGER_BASE_URL`. If your stack uses a custom network, add that same network to `strava-connector`. Port 8000 is the container's internal port; your host's published wger port is not needed for this arrangement.

From your wger stack directory, use the overlay with your normal Compose file (replace the first filename if yours is different):

```sh
docker compose -f docker-compose.yml -f docker-compose.wger.yml pull strava-connector
docker compose -f docker-compose.yml -f docker-compose.wger.yml run --rm strava-connector auth-url
docker compose -f docker-compose.yml -f docker-compose.wger.yml run --rm -i strava-connector auth-complete
# Use the same two -f arguments for preview, map, sync, etc.
docker compose -f docker-compose.yml -f docker-compose.wger.yml run --rm strava-connector preview
docker compose -f docker-compose.yml -f docker-compose.wger.yml run --rm strava-connector map 123 BARBELL_BENCH_PRESS
docker compose -f docker-compose.yml -f docker-compose.wger.yml run --rm strava-connector sync
docker compose -f docker-compose.yml -f docker-compose.wger.yml up -d strava-connector
```

Alternatively, copy the `strava-connector` service and the `strava_connector_state` volume declaration into your existing Compose file. When switching from the standalone deployment, migrate its state volume before starting; the two examples use different named volumes.

For maintenance, stop only `strava-connector`, run commands with the same two `-f` arguments, then start it again. To upgrade either deployment, change its version setting, pull, and run `up -d` for the connector service. Keep the state volume. For a fork or an alternative registry, set `CONNECTOR_IMAGE` (standalone) or `STRAVA_CONNECTOR_IMAGE` (existing stack) to the image repository without its tag.

## Experimental workout image tools

Download `docker-compose.media.yml` from the same release, then run:

```sh
docker compose -f docker-compose.media.yml run --rm preview
docker compose -f docker-compose.media.yml run --rm --service-ports media-login
```

These commands pull `ghcr.io/willtheorangeguy/wger-strava-connector:0.2.1-media`. The first writes sample cards and the comparison catalog to `previews/`. The second opens a browser through `http://localhost:6080/vnc.html`; use its printed temporary viewer password, sign into Strava manually, and stop with Ctrl+C to save the session. No API credentials are needed for these two tools. For a remote Docker host, use the SSH tunnel in the [browser instructions](design/README.md).

The `-media` image is separate from the regular connector image. It contains Chromium and the image renderer. It currently renders synthetic sample data and provides browser login; it does not automatically attach images to future wger exports. Browser photo upload has been proven in a private operator-run test, documented in [live validation](design/LIVE-VALIDATION.md). No public live-upload CLI is included in this release.

## Data and recovery

- Actual logged repetitions and loads are exported; prescribed targets are ignored. Pounds convert to kilograms. Body-weight sets omit a load. Timed sets convert minutes/seconds to whole seconds. Session elapsed time includes rest; active time, calories, heart rate, and GPS are not invented.
- Plates, speed/distance units, unknown weight units, invalid numbers, and fractional repetitions are held for review. Change or correct the source data in wger before exporting. wger notes go into the activity description. Individual notes/supersets/RIR/rest targets have no corresponding field in Strava's strength JSON and are not uploaded as structured metrics.
- Local exercise catalog: 656 identifiers from Strava's upload documentation, checked 2026-10-20. Custom wger exercise names require an explicit supported mapping. Unlisted exercises need a suitable supported equivalent or a future catalog update.
- Once exported, a workout is not uploaded again. Source edits are reported as `changed`; this version does not update or delete existing Strava activities. Source deletion also leaves the exported activity intact. Strava activity visibility follows your Strava account settings.
- Pending upload IDs are persisted and polled after restart. A timeout, server error, or crash while uploading leaves the session `uncertain`; it is **not automatically submitted again**. An external ID is a correlation key, not a guarantee of server-side idempotency.
- To recover an uncertain upload, open the activity on Strava and take its numeric ID from the activity URL. Run `reconcile-activity SESSION_UUID ACTIVITY_ID`. Alternatively, use `reconcile SESSION_UUID UPLOAD_ID` if the upload ID is known. Both verify the external ID before attaching the result. Only if no activity/upload exists, run `retry SESSION_UUID --confirm-no-activity` and then `sync`. Failed uploads also need this explicit retry after correction; do not retry while a Strava job is still processing.
- Rate limits persist a cooldown; daily exhaustion waits for the next UTC day. A rejected 429 is retried in a later cycle. A failed/uncertain OAuth refresh may require authorization again. Commands redact API response bodies and secrets from errors.

Strava accounts authorize their own registered application. New applications have limited athlete capacity; see [Strava's rate limits and athlete capacity](https://developers.strava.com/docs/rate-limits/). Use HTTPS for remote services and follow [Strava's authentication documentation](https://developers.strava.com/docs/authentication/).

## Tests

Developers can build from a checkout using `docker compose -f compose.build.yaml build` and use that same `-f compose.build.yaml` argument for all connector commands. This local-build configuration shares the standalone deployment's project name and state volume, so stop one before starting the other.

With Docker running, check out `wger-addon-harness` beside this repository and run:

```sh
python test_harness.py
# Or: python test_harness.py --wger-harness /path/to/wger-addon-harness
```

This starts/seeds the harness, creates a **temporary dedicated wger account**, adds completed workouts plus unfinished/future controls, and runs the full suite against real wger and a local mock Strava HTTP server. The mock verifies multipart strength JSON. No Strava credentials, Internet forwarding, or real activity uploads are involved. Dedicated users are removed afterward; your demo account and running wger stack remain available. Results are in `reports/junit.xml`.

The harness demo login is `demo`, password **`HarnessDemo123!`**, at `http://localhost:8101`. This is a local sample account; connector tests use a separate generated account/token.

Unit tests without wger:

```sh
pip install -r requirements.lock
pip install --no-deps -e .
pytest -q -m 'not integration'
```

CI runs unit/container checks on pushes and pull requests. A manual workflow run also checks out the public wger harness and runs the integration suite. Publishing a matching GitHub release triggers multi-platform GHCR image builds and attaches version-matched setup downloads. See [RELEASING.md](RELEASING.md).

MIT licensed. See [LICENSE](LICENSE) and [VALIDATION.md](VALIDATION.md).
