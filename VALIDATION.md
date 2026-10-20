# Validation

Release preparation on 2026-10-20: the full local Docker run passed **50 tests in 34.37 seconds** (45 unit/release tests and 5 real-wger/mock-Strava integration cases). Temporary test users and credentials were removed. The public repository is [willtheorangeguy/wger-strava-connector](https://github.com/willtheorangeguy/wger-strava-connector).

The [full hosted validation](https://github.com/willtheorangeguy/wger-strava-connector/actions/runs/39517083648) passed: **50 tests in 3.43 seconds**, plus unit-only checks, deployment/download configuration validation, a container build, and a non-root startup smoke test. GitHub's dependency scan reported no alerts at publication.

Deployment follow-up on 2026-10-20: the default Compose file and the existing-wger overlay now pull GHCR images without a source checkout. A clean directory containing only `docker-compose.yml` and `.env` successfully ran `status` with the local image override and `--pull never`; its isolated test volume was removed afterward. Repository templates and generated release downloads passed Compose validation. Release rendering is tested for stable/prerelease versions and forked image names. This check preceded GHCR publication and used the local image override.

Follow-up tests: **45 unit/release tests passed in 3.82 seconds**, with the 5 integration cases deselected because the application code did not change. The existing-wger overlay also validated when merged with the actual harness Compose file, including a shared network with `web`. Workflow lint and `git diff --check` passed.

On 2026-10-20, the initial `python test_harness.py` run completed successfully on Windows with Docker Desktop: **48 passed in 16.62 seconds** (43 unit/release tests, 5 integration cases). The fixtures select wger's actual Bench Press and Plank exercises. JUnit results are saved locally in `reports/junit.xml`; the initial runner log is `reports/local-test.log`, and release preparation uses `reports/release-test.log`. All are ignored by Git.

Covered real wger API reads and a source edit, finished/unfinished/future sessions, native multipart JSON with distinct exercises, repetitions and actual loads, lb → kg conversion, 90-second timed sets, local UTC offset, missing mappings, asynchronous upload status, persisted restart state, lost committed responses, recovery by upload ID and activity ID, refusal to attach a different workout, edit reporting, token rotation, refresh uncertainty, state-volume locking, pagination origin checks, and rate-limit cooldowns.

Standalone and existing-wger Compose examples validated successfully with dummy credentials. GitHub workflows passed actionlint 1.7.12. The rebuilt container's CLI help and fresh-state `status` command passed; the container runs as UID 10001 and can initialize its state volume. Temporary harness users and credentials were removed after the tests. These checks preceded GitHub publication.

The API contract follows Strava's [JSON strength upload documentation](https://developers.strava.com/docs/uploads/), checked 2026-10-20, and the wger `2.8.0-dev.1` image pinned in the sibling harness. This is not a live Strava acceptance test. The exercise catalog is a snapshot of the identifiers documented on that date.

Tests use real wger HTTP endpoints with a generated dedicated account, and a local mock Strava HTTP server. No real Strava credentials or activities are used. The harness demo credentials are documented in README.md; temporary test credentials and reports are ignored by Git.
