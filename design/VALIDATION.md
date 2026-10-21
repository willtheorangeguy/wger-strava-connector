# Prototype validation

Validated on Docker Desktop (Linux containers) on October 20, 2026.

- Existing connector unit suite: 45 passed, 1 skipped, 5 integration cases deselected. Command: `docker compose -f compose.test.yaml run --rm --no-deps test -q -m 'not integration'`.
- Media suite: 15 passed in 48.49 seconds. Command: `docker compose -f compose.media.test.yaml run --rm --no-deps test`.
- Real Chromium rendered both themes twice with byte-identical PNGs and checked all four individual cards are 1080×1080.
- Real Chromium uploaded both images to the mock activity, reopened it, restarted with its saved login and prevented duplicate uploads. Wrong accounts, expired login and an ambiguous save were also exercised.
- The headful browser and temporary noVNC viewer started without a host display as UID 10001, using an unwritable shared home directory, then shut down cleanly on SIGTERM.

Hosted checks for commit `3d285cf`: [connector tests](https://github.com/willtheorangeguy/wger-strava-connector/actions/runs/39526234479) and [media prototype tests](https://github.com/willtheorangeguy/wger-strava-connector/actions/runs/39526234512). The media workflow also builds the prototype container and renders the design previews; its artifact contains PNGs and the JUnit report.

These tests validate the local renderer and mock browser behavior. They do not validate live Strava page selectors, photo processing or browser login policy. No real Strava account or activity was used. Production workout exports do not invoke this prototype.

Visual approval and a live browser feasibility check remain required before implementing the production attachment worker. See [the design milestone](README.md).
