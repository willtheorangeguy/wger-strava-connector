# Changelog

## 0.2.1 — 2026-10-21

- Replace 19 weight comparison illustrations with more recognizable animal profiles, vehicles, machinery, landmarks, and Saturn V details while retaining the shared palette and canvas.
- Correct pickup windows, remove the forklift load, contain whale shark spots within the body, and level the excavator base with a reversed, smooth bucket.
- Add a side-view airliner and a carrier silhouette with parked aircraft, bridge windows, and hull details.
- Credit the carrier silhouette by TheFrenchKing under CC BY-SA 4.0, with source and adaptation details bundled in the media assets.
- Refresh the illustrated catalog preview and advance the connector and experimental-media setup defaults to 0.2.1.

## 0.2.0 — 2026-10-20

- Add experimental dark workout-summary cards with enlarged front/back muscle diagrams and 30 original illustrated weight comparisons.
- Add deterministic, offline Chromium rendering with a bundled font, consistent kg/lb comparison selection, and zero-load handling.
- Add a temporary browser login viewer for headless Docker hosts, private saved sessions, and explicit preservation of session-only authentication cookies.
- Verify two sample image attachments on one consenting account's private Strava activity, including persistence after browser restart. Automated browser tests use a local mock website.
- Publish a separate `0.2.0-media` container and image-only Compose download alongside the regular connector container, for Linux amd64 and arm64.
- Gate release publishing on connector and media tests; attach version-matched setup files and card previews.
- Automatic image generation/attachment for completed wger exports is not included yet. The existing API export flow remains independent of the media prototype.

## 0.1.0 — 2026-10-20

- Export completed wger sessions as Strava strength JSON, with mapped exercises, actual repetitions/load, and timed sets.
- Docker deployment and an overlay for an existing wger Compose stack.
- Interactive OAuth consent with nonce validation and durable rotating tokens.
- Upload journal, asynchronous processing, explicit recovery, account binding, and rate-limit cooldowns.
- Unit tests and real-wger/mock-Strava integration tests using the standalone wger addon harness.
- CI checks and release-triggered multi-platform GHCR publishing workflow.
- Copy-and-run GHCR Compose/environment files, an image-based existing-wger overlay, and version-matched release setup downloads.
