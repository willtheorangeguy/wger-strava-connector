# Validation

Live Strava upload fix, October 21, 2026: rebuilt the local wger image with UTC
`Z` serialization for activity and optional set timestamps, preserving fractional
seconds. Explicit retries retain failed-attempt history and use fresh file IDs;
successful/processing remote jobs cannot be retried. Queued retries revalidate
source values and mappings. Unit checks passed **90 tests**, with one media
collection skip and six integration cases deselected.
The complete real-wger/mock-Strava run then passed **96 tests**, with one media
collection skip. Coverage includes timestamp offsets and precision, timed/bodyweight
sets, cached failures, explicit retry identifiers, preserved attempt history,
restart, source revalidation, reconciliation, token rotation, and duplicate
prevention. Reports: `reports/live-upload-fix-unit.xml` and `reports/junit.xml`.
The local `.env` selects the corrected `wger-strava-connector:local` image for
normal Compose commands; the published registry release has not been changed.

One authorized live test used a local mock wger HTTP API and the normal connector
engine against real Strava. The workout is dated **2026-10-21 in America/Edmonton**
and titled **TEST — wger connector mock workout — DELETE ME**. Activity
`20682924427` was processed successfully. It contains four uploaded sets: two
bench-press sets (kg and lb inputs), a bodyweight squat set, and a 45-second plank.
Strava API readback confirmed the exact title, local date, WeightTraining type,
15-minute elapsed time, external ID, and exactly one matching activity. A repeated
sync submitted nothing. The mock source/export journal is isolated from normal
accounts; existing OAuth state was used under an exclusive lock, without copying
tokens. SparkyFitness syncing was paused for the test and resumed afterward.
The test activity remains for the operator to inspect and remove. Mobile
exercise-log rendering was not independently verified. Private fixture, payload,
journal, and verification artifacts are ignored under `runtime/`.

Companion-service follow-up, October 21, 2026: all three regular Compose setups
explicitly run `watch`, restart unless stopped, and retain `/data`. The overlay
was merged with the actual wger harness and its shared main-service network checked.
The unit suite passed **84 tests** (one media collection skip; five integration
cases deselected), including new watcher tests that start before wger is available,
observe a workout complete after startup, upload it once, poll its asynchronous
result, and retain the exported journal. No real Strava uploads were performed.
Report: `reports/watch-unit.xml`.

[Release v0.1.0](https://github.com/willtheorangeguy/wger-strava-connector/releases/tag/v0.1.0) published successfully on 2026-10-20. Its [release workflow](https://github.com/willtheorangeguy/wger-strava-connector/actions/runs/39517436921) passed version validation, tests, multi-platform GHCR publishing, and setup download attachment. The four release assets are `docker-compose.yml`, `env.example`, `docker-compose.wger.yml`, and `wger.env.example`.

Anonymous GHCR manifest requests returned HTTP 200 for `0.1.0`, `0.1`, and `latest`. All three tags resolve to the same amd64/arm64 OCI index: `sha256:2374beda9d9fe2b73ad9ec43a4f6b9150d6057bb1d555ff1b99e64afc9dd6473`. A fresh directory containing only the downloaded `docker-compose.yml` and `env.example` renamed to `.env` successfully pulled and started the published image, initialized its state volume, and ran `status`. Its isolated test volume was removed afterward. This smoke test made no authenticated wger or Strava API calls.

Release preparation on 2026-10-20: the full local Docker run passed **50 tests in 34.37 seconds** (45 unit/release tests and 5 real-wger/mock-Strava integration cases). Temporary test users and credentials were removed. The public repository is [willtheorangeguy/wger-strava-connector](https://github.com/willtheorangeguy/wger-strava-connector).

The [full hosted validation](https://github.com/willtheorangeguy/wger-strava-connector/actions/runs/39517083648) passed: **50 tests in 3.43 seconds**, plus unit-only checks, deployment/download configuration validation, a container build, and a non-root startup smoke test. GitHub's dependency scan reported no alerts at publication.

Deployment follow-up on 2026-10-20: the default Compose file and the existing-wger overlay now pull GHCR images without a source checkout. A clean directory containing only `docker-compose.yml` and `.env` successfully ran `status` with the local image override and `--pull never`; its isolated test volume was removed afterward. Repository templates and generated release downloads passed Compose validation. Release rendering is tested for stable/prerelease versions and forked image names. This check preceded GHCR publication and used the local image override.

Follow-up tests: **45 unit/release tests passed in 3.82 seconds**, with the 5 integration cases deselected because the application code did not change. The existing-wger overlay also validated when merged with the actual harness Compose file, including a shared network with `web`. Workflow lint and `git diff --check` passed.

On 2026-10-20, the initial `python test_harness.py` run completed successfully on Windows with Docker Desktop: **48 passed in 16.62 seconds** (43 unit/release tests, 5 integration cases). The fixtures select wger's actual Bench Press and Plank exercises. JUnit results are saved locally in `reports/junit.xml`; the initial runner log is `reports/local-test.log`, and release preparation uses `reports/release-test.log`. All are ignored by Git.

Covered real wger API reads and a source edit, finished/unfinished/future sessions, native multipart JSON with distinct exercises, repetitions and actual loads, lb → kg conversion, 90-second timed sets, local UTC offset, missing mappings, asynchronous upload status, persisted restart state, lost committed responses, recovery by upload ID and activity ID, refusal to attach a different workout, edit reporting, token rotation, refresh uncertainty, state-volume locking, pagination origin checks, and rate-limit cooldowns.

Standalone and existing-wger Compose examples validated successfully with dummy credentials. GitHub workflows passed actionlint 1.7.12. The rebuilt container's CLI help and fresh-state `status` command passed; the container runs as UID 10001 and can initialize its state volume. Temporary harness users and credentials were removed after the tests. These checks preceded GitHub publication.

The API contract follows Strava's [JSON strength upload documentation](https://developers.strava.com/docs/uploads/), checked 2026-10-20, and the wger `2.8.0-dev.1` image pinned in the sibling harness. This is not a live Strava acceptance test. The exercise catalog is a snapshot of the identifiers documented on that date.

Tests use real wger HTTP endpoints with a generated dedicated account, and a local mock Strava HTTP server. No real Strava credentials or activities are used. The harness demo credentials are documented in README.md; temporary test credentials and reports are ignored by Git.

## Automatic image cards — October 21, 2026

The export engine now snapshots the exact uploaded sets and atomically enqueues image work after the activity ID is known. Queue failures retain successful workout state. A separate Chromium worker attaches two actual-data cards and journals intent before file selection. Existing receipts prevent a second upload, including receipts left uncertain after a crash. The worker checks the logged-in athlete, activity ownership and unchanged activity fields before and after Save. The renderer uses local fonts/artwork; total volume is external kg times repetitions, converted for display. Unrecorded body mass and timed holds do not add lifting volume.

A new clearly labeled synthetic workout was uploaded to the consenting account, dated October 21 in America/Edmonton: 900 seconds, four sets, three exercises, rounded total 1,245 lb. The export created its image job automatically. Both generated PNGs persisted on the activity after browser restart, and Only You visibility was retained. Source fixtures, upload/attachment journals, image hashes, screenshots and destination details remain under ignored `runtime/` directories. The normal source journal and mock source journal were kept separate; API tokens were used from the existing authorized store without making token copies.

Live testing caught a stale Chromium profile lock, an editor prompt that disappears after images exist, and privacy controls that hydrate after the Save button. Verification now waits for the relevant controls and loaded thumbnails. The wger pre-Save hold was inspected read-only; no photos had persisted, so its prior receipt was retained as an attempt record before one explicit recovery. The recovered job saved successfully and was verified after browser restart. No extra workout activity was created by recovery.

Automatic card generation is enabled in both local connector configs, and both companion workers run persistently. The configured SparkyFitness source watcher is running. The standalone wger config still has no source token or Strava client credentials; its real-source watcher was not started. The wger mock upload reused the consenting account's existing OAuth store in isolation.

Validation results for this change: full core/harness suites passed (SparkyFitness 165, wger 98; each skipped the separate media suite). The additional image-queue failure test passed in each project. Browser suites passed their existing cases after rerunning one short login timeout under load; all three new production-worker browser regressions passed in both projects after fixing the PNG/JavaScript test fixtures. Successful Save, post-Save uncertainty, immutable queue replay, persisted photos and prevention of repeat file selection are covered. The live Strava checks above were separate from the intercepted/mock browser tests.

## Muscle metadata regression fix — October 21, 2026

Both engines now preserve primary and secondary anatomy through the durable media job into the rendered summary. SparkyFitness reads only completed exercise snapshots. wger fetches exercise-info for the distinct logged exercise IDs of a new export and translates its English/Latin muscle names. A shared normalization table maps explicit anatomy to supported diagram regions; unknown labels are retained for diagnosis, not guessed. A muscle that is primary anywhere in the workout takes precedence over secondary classification elsewhere. Failed optional wger anatomy reads do not prevent a strength upload.

Regression coverage exercises engine synchronization through the saved image outbox, excludes unfinished exercise metadata, verifies name aliases and unknown labels, and checks actual CSS fill colors on mirrored front/back SVG paths with Chromium. Both projects' browser color tests passed. A separate read-only preview used the configured SparkyFitness instance's real native Barbell Squat workout: primary calves/hamstrings/quads; secondary glutes/lower back; no unmapped source names. The rendered result was inspected visually and is stored privately under ignored `runtime/native-muscle-preview/`. No Strava activity or existing photos were changed by this verification. Existing immutable export jobs and uploaded images remain unchanged; the fix applies to new exports.

Final checks for the muscle fix: SparkyFitness core/harness 170 passed, wger core/harness 105 passed; each skipped the three separately run browser modules. The new Chromium color regression passed independently in both projects. Local images were rebuilt, both image workers restarted, and the configured SparkyFitness core watcher restarted.

## Release v0.3.0

Release includes native strength upload/recovery fixes and automatic workout images with source muscle highlights. Core/harness and browser verification are recorded above. Downloadable media setup now includes the persistent worker and configurable shared state volume. No production credentials or private runtime artifacts are packaged.
