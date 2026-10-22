# Workout images

Set `MEDIA_ENABLED=true` and `MEDIA_UNITS=lb` (or `kg`) in `.env`, then recreate the core connector. Each new successful export creates an immutable image job. The activity description also includes total external weight times repetitions; timed holds and unrecorded body weight add no volume.

Build the local media image from this checkout, then sign into the same athlete once:

```sh
docker compose -f compose.media.yaml build
docker compose -f compose.media.yaml run --rm --service-ports media-login
docker compose -f compose.media.yaml up -d media-worker
docker compose -f compose.media.yaml run --rm --no-deps media-worker status
```

The standalone core connector must already have created its state volume. The source `compose.media.yaml` fixes the external volume name to `wger-strava-connector_state`. For an existing source stack, enable `STRAVA_MEDIA_ENABLED=true` and `STRAVA_MEDIA_UNITS=lb`, then override the worker's external volume with the actual stack volume name.

```yaml title="compose.media.override.yaml"
volumes:
  connector_state:
    external: true
    name: fitness_strava_connector_state
```

Replace `fitness_strava_connector_state` with the volume created by your stack. Add both `-f compose.media.yaml -f compose.media.override.yaml` to every media command for that deployment. This source file does not read `CONNECTOR_STATE_VOLUME`; that variable belongs to the release-oriented media example.

Stop `media-worker` before interactive login, and start it again afterwards. Browser cookies are separate from API OAuth. The companion shares the core state volume but never opens its SQLite database. It attaches two 1080 x 1080 cards generated from the exact exported sets, without changing activity fields. Missing muscle metadata is shown as unavailable. Existing exports are not backfilled automatically.

Jobs and receipts persist under `/data/media`. An interrupted file selection or Save is held as `uncertain`; inspect the activity and receipt before any manual recovery. Never delete a receipt simply to retry an upload. Browser login expiry leaves new jobs pending; log in again to resume. Existing activity photos are held for review. API workout exports continue independently of browser failures.

Automatic images are implemented in source version 0.3.0. At the 2026-10-22 documentation check, that version was not yet a published release. The mock-only attachment helper retains its origin restriction.

Muscle highlighting uses wger's exercise-info API (`muscles` and `muscles_secondary`). Source names and Latin anatomy names are translated into the diagram's regions. Primary takes precedence when an area is also secondary in another exercise. Unknown names remain unhighlighted and are recorded under `unmapped_muscles` in the image job; wger metadata fetch failures are recorded under `unavailable_exercises` and do not block the workout upload. Previously attached image files are not rewritten automatically.

## Card previews and browser login

Build the local media image from this checkout, then sign into the same athlete once:

```sh
docker compose -f compose.media.yaml run --rm preview
docker compose -f compose.media.yaml run --rm --service-ports media-login
```

These commands use the locally built media image. The first writes sample cards and the comparison catalog to `design/previews/`. The second opens a browser through `http://localhost:6080/vnc.html`; use its printed temporary viewer password, sign into Strava manually, and stop with Ctrl+C to save the session. No API credentials are needed for these two tools. For a remote Docker host, use the SSH tunnel in the [browser instructions](https://github.com/willtheorangeguy/wger-strava-connector/blob/HEAD/design/README.md).

The `-media` image contains Chromium, the image renderer and the automatic worker. Browser login is separate from API OAuth and must use the same athlete account.

## Headless server login

Open a tunnel from your laptop before using the loopback-only viewer on a remote Docker host:

```sh
ssh -N -L 6080:127.0.0.1:6080 user@your-server
```

Use the host and user for your server. Open the viewer at `http://localhost:6080/vnc.html`, enter the temporary password printed by `media-login`, and complete Strava login and MFA yourself. Stop gracefully to save session cookies. The worker and interactive login require exclusive access to the same profile.

## Worker commands

| Command | Example | Result |
| --- | --- | --- |
| `status` | `docker compose -f compose.media.yaml run --rm --no-deps media-worker status` | Activity ID and persisted receipt state, or pending. |
| `once` | `docker compose -f compose.media.yaml run --rm media-worker once` | Process eligible jobs once. Stop the resident worker first. |
| `watch` | `docker compose -f compose.media.yaml up -d media-worker` | Poll every 60 seconds using the service default. |

The Python worker also accepts `--data` (default `/data`) and `--profile` (default `/browser-profile`). The renderer accepts `--output`, default `/previews`.

## Artwork and comparison rules

The selected dark cards use original schematic anatomy, indicating source primary/secondary metadata rather than intensity. Comparison masses range from a hippopotamus to the Great Pyramid. Selection uses unrounded kg volume and the nearest reference, choosing the lighter on a tie. Display units preserve the subject; zero recorded external load has no equivalence. The 12,000 lb demo is synthetic data.

Inter Variable v4.1 is bundled under the SIL Open Font License. The carrier illustration adapts TheFrenchKing's silhouette under CC BY-SA 4.0; other artwork is original. Retain the [carrier attribution notice](https://github.com/willtheorangeguy/wger-strava-connector/blob/HEAD/src/wger_strava/media/assets/carrier-LICENSE.txt) when reusing that illustration. Historical [design review](https://github.com/willtheorangeguy/wger-strava-connector/blob/HEAD/design/README.md) and [live validation](https://github.com/willtheorangeguy/wger-strava-connector/blob/HEAD/design/LIVE-VALIDATION.md) remain in the repository, with older milestones identified as historical.
