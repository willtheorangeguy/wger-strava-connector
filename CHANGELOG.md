# Changelog

## 0.1.0 — Unreleased

- Export completed wger sessions as Strava strength JSON, with mapped exercises, actual repetitions/load, and timed sets.
- Docker deployment and an overlay for an existing wger Compose stack.
- Interactive OAuth consent with nonce validation and durable rotating tokens.
- Upload journal, asynchronous processing, explicit recovery, account binding, and rate-limit cooldowns.
- Unit tests and real-wger/mock-Strava integration tests using the standalone wger addon harness.
- CI checks and release-triggered multi-platform GHCR publishing workflow.
- Copy-and-run GHCR Compose/environment files, an image-based existing-wger overlay, and version-matched release setup downloads.
