# Workout images

Set `MEDIA_ENABLED=true` and `MEDIA_UNITS=lb` (or `kg`) in `.env`, then recreate the core connector. Each new successful export creates an immutable image job. The activity description also includes total external weight times repetitions; timed holds and unrecorded body weight add no volume.

Download `docker-compose.media.yml` from the same release beside your standalone `.env`, then sign into the same Strava account once:

```sh
docker compose -f docker-compose.media.yml pull
docker compose -f docker-compose.media.yml run --rm --service-ports media-login
docker compose -f docker-compose.media.yml up -d media-worker
docker compose -f docker-compose.media.yml run --rm --no-deps media-worker status
```

The standalone core connector must already have created its state volume. For an existing source stack, set `STRAVA_MEDIA_ENABLED=true` and `STRAVA_MEDIA_UNITS=lb` in that stack's environment, and set `CONNECTOR_STATE_VOLUME` beside the media Compose file to the actual `<stack>_strava_connector_state` volume name. For source-checkout builds, use `compose.media.yaml` in the commands above and build `media-worker` first.

Stop `media-worker` before interactive login, and start it again afterwards. Browser cookies are separate from API OAuth. The companion shares the core state volume but never opens its SQLite database. It attaches two 1080 x 1080 cards generated from the exact exported sets, without changing activity fields. Missing muscle metadata is shown as unavailable. Existing exports are not backfilled automatically.

Jobs and receipts persist under `/data/media`. An interrupted file selection or Save is held as `uncertain`; inspect the activity and receipt before any manual recovery. Never delete a receipt simply to retry an upload. Browser login expiry leaves new jobs pending; log in again to resume. Existing activity photos are held for review. API workout exports continue independently of browser failures.

Automatic images are included in v0.3.0. Older releases provide only preview/login tools. The mock-only attachment helper retains its origin restriction.

Muscle highlighting uses explicit source metadata: SparkyFitness's completed-exercise snapshots or wger's exercise-info API (`muscles` and `muscles_secondary`). Source names and Latin anatomy names are translated into the diagram's regions. Primary takes precedence when an area is also secondary in another exercise. Uncompleted SparkyFitness exercises are excluded. Unknown names remain unhighlighted and are recorded under `unmapped_muscles` in the image job; wger metadata fetch failures are recorded under `unavailable_exercises` and do not block the workout upload. Previously attached image files are not rewritten automatically.

## Card previews and browser login

Download `docker-compose.media.yml` from the same release, then run:

```sh
docker compose -f docker-compose.media.yml run --rm preview
docker compose -f docker-compose.media.yml run --rm --service-ports media-login
```

These commands pull `ghcr.io/willtheorangeguy/wger-strava-connector:0.3.0-media`. The first writes sample cards and the comparison catalog to `previews/`. The second opens a browser through `http://localhost:6080/vnc.html`; use its printed temporary viewer password, sign into Strava manually, and stop with Ctrl+C to save the session. No API credentials are needed for these two tools. For a remote Docker host, use the SSH tunnel in the [browser instructions](https://github.com/willtheorangeguy/wger-strava-connector/blob/HEAD/design/README.md).

The `-media` image contains Chromium, the image renderer and the automatic worker described below. Browser login is separate from API OAuth and must use the same athlete account.

## Headless server login

Open a tunnel from your laptop before using the loopback-only viewer on a remote Docker host:

```sh
ssh -N -L 6080:127.0.0.1:6080 user@your-server
```

Use the host and user for your server. Open the viewer at `http://localhost:6080/vnc.html`, enter the temporary password printed by `media-login`, and complete Strava login and MFA yourself. Stop gracefully to save session cookies. The worker and interactive login require exclusive access to the same profile.

## Worker commands

| Command | Example | Result |
| --- | --- | --- |
| `status` | `docker compose -f docker-compose.media.yml run --rm --no-deps media-worker status` | Activity ID and persisted receipt state, or pending. |
| `once` | `docker compose -f docker-compose.media.yml run --rm media-worker once` | Process eligible jobs once. Stop the resident worker first. |
| `watch` | `docker compose -f docker-compose.media.yml up -d media-worker` | Poll every 60 seconds using the service default. |

The Python worker also accepts `--data` (default `/data`) and `--profile` (default `/browser-profile`). The renderer accepts `--output`, default `/previews`.

## Artwork and comparison rules

The selected dark cards use original schematic anatomy, indicating source primary/secondary metadata rather than intensity. Comparison masses range from a hippopotamus to the Great Pyramid. Selection uses unrounded kg volume and the nearest reference, choosing the lighter on a tie. Display units preserve the subject; zero recorded external load has no equivalence. The 12,000 lb demo is synthetic data.

Inter Variable v4.1 is bundled under the SIL Open Font License. Original anatomy and comparison art use the repository's MIT license. Historical [design review](https://github.com/willtheorangeguy/wger-strava-connector/blob/HEAD/design/README.md) and [live validation](https://github.com/willtheorangeguy/wger-strava-connector/blob/HEAD/design/LIVE-VALIDATION.md) remain in the repository, with older milestones identified as historical.
