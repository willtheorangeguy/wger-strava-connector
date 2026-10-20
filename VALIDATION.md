# Validation

On 2026-10-20, the final `python test_harness.py` run completed successfully on Windows with Docker Desktop: **48 passed in 16.62 seconds** (43 unit/release tests, 5 integration cases). The fixtures select wger's actual Bench Press and Plank exercises. JUnit results are saved locally in `reports/junit.xml`; the complete runner log is `reports/local-test.log`. Both are ignored by Git.

Covered real wger API reads and a source edit, finished/unfinished/future sessions, native multipart JSON with distinct exercises, repetitions and actual loads, lb → kg conversion, 90-second timed sets, local UTC offset, missing mappings, asynchronous upload status, persisted restart state, lost committed responses, recovery by upload ID and activity ID, refusal to attach a different workout, edit reporting, token rotation, refresh uncertainty, state-volume locking, pagination origin checks, and rate-limit cooldowns.

Standalone and existing-wger Compose examples validated successfully with dummy credentials. GitHub workflows passed actionlint 1.7.12. The rebuilt container's CLI help and fresh-state `status` command passed; the container runs as UID 10001 and can initialize its state volume. Temporary harness users and credentials were removed after the tests. No GitHub repository or release has been created for this addon yet; hosted CI and GHCR publication have not run.

The API contract follows Strava's [JSON strength upload documentation](https://developers.strava.com/docs/uploads/), checked 2026-10-20, and the wger `2.8.0-dev.1` image pinned in the sibling harness. This is not a live Strava acceptance test. The exercise catalog is a snapshot of the identifiers documented on that date.

Tests use real wger HTTP endpoints with a generated dedicated account, and a local mock Strava HTTP server. No real Strava credentials or activities are used. The harness demo credentials are documented in README.md; temporary test credentials and reports are ignored by Git.
