# Workout images: review milestone

Branch: `feat/workout-summary-images`. This is a design/browser prototype, **not integrated into production sync**. No new release is published by this milestone.

Two proposed directions, each with a workout summary and an elephant comparison:

- Light: wger navy/blue, white anatomy panel, restrained statistics.
- Dark: deep navy, brighter muscle highlights, a stronger feed contrast.

![Light and dark card concepts](previews/concepts.png)

Individual previews: [light summary](previews/light-summary.png), [light comparison](previews/light-comparison.png), [dark summary](previews/dark-summary.png), [dark comparison](previews/dark-comparison.png).

The sample 12,000 lb total is synthetic design data. The elephant is an approximate visual analogy, not a biological measurement. The anatomy is original schematic vector artwork: primary/secondary colors identify muscle metadata, not activation intensity. No Hevy artwork is bundled.

Inter Variable v4.1 is bundled from the [official Inter repository](https://github.com/rsms/inter/tree/v4.1), with its SIL Open Font License in `src/wger_strava/media/assets/INTER-LICENSE.txt`. All anatomy and elephant SVG paths are original project assets under this repository's MIT license.

## Render the concepts

```sh
docker compose -f compose.media.yaml build
docker compose -f compose.media.yaml run --rm preview
```

Four 1080×1080 PNGs and a combined `concepts.png` review sheet are written to `design/previews/`. Templates and fonts are entirely local; the renderer blocks network requests. The Debian/Python base is pinned by digest. Playwright 1.63.0 installs only its matching Chromium build, used for both interactive and headless operation.

## Login on a headless Docker host

```sh
docker compose -f compose.media.yaml run --rm --service-ports media-login
```

Open `http://localhost:6080/vnc.html`. Enter the temporary viewer password printed by the command, then sign into Strava **inside that browser**. You handle password entry, MFA and any login challenge. No Strava password goes in `.env`. Stop the service with Ctrl+C when done; the Chromium profile remains in its named volume.

For a remote server, first open an SSH tunnel from your laptop:

```sh
ssh -N -L 6080:127.0.0.1:6080 user@your-server
```

Open the same localhost viewer URL on your laptop. The remote server needs no desktop, display or GPU. Only this temporary login service publishes a port, bound to loopback. A future worker will reuse the volume headlessly. An exclusive profile lock prevents login and automation from opening the same profile concurrently. Browser state is private authentication material; never commit, share, or place it in a release asset.

## Test the browser proof

```sh
docker compose -f compose.media.test.yaml up -d --wait mock-strava-web
docker compose -f compose.media.test.yaml run --rm test
docker compose -f compose.media.test.yaml down
```

This uses real Chromium with a mock website. It exercises file selection, saving two PNGs, reopening the activity, persistent login across browser restart, wrong-account rejection, duplicate prevention, and uncertain-save recovery. It does not use Strava credentials or forward requests to Strava. The mock DOM is a behavioral fixture; it is **not evidence that the live Strava selectors work**.

`attach_mock` explicitly rejects live Strava URLs. A live adapter and its ownership/media selectors must be verified after a user supplies an interactive login and agrees on a test activity. Do not claim automatic Strava attachment is complete until that live test passes.

## Approval gates and next work

The agreed plan requires visual review of these two concepts before implementing the full media worker. After a style is chosen and live browser feasibility is established, add the durable outbox, wger muscle metadata snapshots, automatic attachment to confirmed export IDs, recovery/status commands, both architecture builds and GHCR release integration. Keep current API exports independent of browser/media failures.
