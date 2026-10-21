# Prototype validation

Validated on Docker Desktop (Linux containers) on October 20, 2026.

- Connector and comparison unit suite: 82 passed, 1 skipped, 5 integration cases deselected (2.72 seconds). Command: `docker compose -f compose.test.yaml run --rm --no-deps test -q -m 'not integration'`.
- Media suite: 16 passed in 71.59 seconds. Command: `docker compose -f compose.media.test.yaml run --rm --no-deps test`.
- Real Chromium rendered both themes twice with byte-identical PNGs and checked all four individual cards are 1080×1080.
- Real Chromium uploaded both images to the mock activity, reopened it, restarted with its saved login and prevented duplicate uploads. Wrong accounts, expired login and an ambiguous save were also exercised.
- The headful browser and temporary noVNC viewer started without a host display as UID 10001, using an unwritable shared home directory, then shut down cleanly on SIGTERM.
- All 30 references are reachable, preserve selection between kg and lb, and have valid local SVG artwork. Nearest-weight ties, small fractions, zero load and above-catalog multiples are covered.
- Real Chromium checked every comparison title and large number fits its card, and verified the selected dark summary uses 510 px muscle diagrams with no footer tagline.

Initial browser-milestone hosted checks for commit `3d285cf`: [connector tests](https://github.com/willtheorangeguy/wger-strava-connector/actions/runs/39526234479) and [media prototype tests](https://github.com/willtheorangeguy/wger-strava-connector/actions/runs/39526234512). Current branch checks appear in [GitHub Actions](https://github.com/willtheorangeguy/wger-strava-connector/actions). The media workflow also builds the prototype container and renders the design previews; its artifact contains PNGs and the JUnit report.

The automated suites validate the local renderer and mock browser behavior. They do not validate live Strava page selectors, photo processing or browser login policy. A subsequent, separate [live feasibility test](LIVE-VALIDATION.md) verified saved-session reuse and both sample image attachments on a nominated private activity. Production workout exports do not invoke this prototype.

The dark visual direction has been approved and revised, and live browser feasibility has been demonstrated for one account. The production attachment worker remains to be implemented. See [the design milestone](README.md).
