# Testing

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

CI runs unit/container checks on pushes and pull requests. A manual workflow run also checks out the public wger harness and runs the integration suite. Publishing a matching GitHub release triggers multi-platform GHCR image builds and attaches version-matched setup downloads. See [RELEASING.md](https://github.com/willtheorangeguy/wger-strava-connector/blob/HEAD/RELEASING.md).

MIT licensed. See [LICENSE](https://github.com/willtheorangeguy/wger-strava-connector/blob/HEAD/LICENSE) and [VALIDATION.md](https://github.com/willtheorangeguy/wger-strava-connector/blob/HEAD/VALIDATION.md).

## Browser tests

```sh
docker compose -f compose.media.test.yaml build test
docker compose -f compose.media.test.yaml up -d --wait mock-strava-web
docker compose -f compose.media.test.yaml run --rm test
docker compose -f compose.media.test.yaml down
```

Browser tests use Chromium against a local mock, covering login persistence, identity checks, image selection and uncertain outcomes. They do not establish live selector compatibility for every Strava account. Existing validation records describe historical runs; this documentation change does not rerun live account uploads.
