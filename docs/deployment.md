# Deployment

Current source version `0.3.0` was not yet a published release on 2026-10-22. The overlay below describes the checked-in service arrangement. To use it with a local image, build the core with `compose.build.yaml`, then set `STRAVA_CONNECTOR_IMAGE=wger-strava-connector` and `STRAVA_CONNECTOR_VERSION=local` in the source stack's `.env`. Do not pull that local image. Published deployments must use the matched files/version from an existing release.

Copy [`examples/docker-compose.wger.yml`](https://github.com/willtheorangeguy/wger-strava-connector/blob/HEAD/examples/docker-compose.wger.yml) beside your existing wger Compose file, and add the settings from [`examples/wger.env.example`](https://github.com/willtheorangeguy/wger-strava-connector/blob/HEAD/examples/wger.env.example) to that stack's `.env`. Published releases provide matched overlay/environment downloads; the current source deployment needs the local build described above.

The default URL `http://web:8000` assumes your wger service is named `web` and both services use the default Compose network. If your service has another name, change `STRAVA_WGER_BASE_URL`. If your stack uses a custom network, add that same network to `strava-connector`. Port 8000 is the container's internal port; your host's published wger port is not needed for this arrangement.

From your wger stack directory, use the overlay with your normal Compose file (replace the first filename if yours is different):

```sh
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

## Watcher operation

`docker compose -f compose.build.yaml up -d` runs `watch` continuously with `restart: unless-stopped`. It checks immediately and sleeps 900 seconds between cycles by default. The 300-second settling delay normally makes discovery take 5–20 minutes after completion, plus asynchronous Strava processing. API failures are logged and reconsidered next cycle; ambiguous writes remain held for manual recovery.

```sh
docker compose -f compose.build.yaml logs -f connector
```

## State and backups

The standalone `state` volume contains `/data/state.sqlite3` and its process lock. The database has JSON-backed `settings` and `exports` tables. Stop the connector before taking a consistent volume backup. Restore that backup to the same deployment before starting it. Do not initialize a replacement journal for an account that already has exports.

Image queues and receipts live in the same core volume under `/data/media`; browser authentication lives in the media Compose project's `browser_profile` volume. Back up both with the worker and login service stopped.
