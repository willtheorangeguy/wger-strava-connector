# Usage

Stop the watcher before opening its state from a one-off command. After first-time authorization, use this maintenance sequence:

```sh
docker compose -f compose.build.yaml stop connector
docker compose -f compose.build.yaml run --rm connector preview
docker compose -f compose.build.yaml run --rm connector status
docker compose -f compose.build.yaml up -d
```

## Data and recovery

- Actual logged repetitions and loads are exported; prescribed targets are ignored. Pounds convert to kilograms. Body-weight sets omit a load. Timed sets convert minutes/seconds to whole seconds. Session elapsed time includes rest; active time, calories, heart rate, and GPS are not invented.
- Activity and optional set timestamps use UTC `Z` suffixes, preserving fractional seconds and the athlete's local display offset. Live Strava JSON processing rejects otherwise equivalent `+00:00` timestamps.
- Plates, speed/distance units, unknown weight units, invalid numbers, and fractional repetitions are held for review. Change or correct the source data in wger before exporting. wger notes go into the activity description. Individual notes/supersets/RIR/rest targets have no corresponding field in Strava's strength JSON and are not uploaded as structured metrics.
- Local exercise catalog: 656 identifiers from Strava's upload documentation, checked 2026-10-20. Custom wger exercise names require an explicit supported mapping. Unlisted exercises need a suitable supported equivalent or a future catalog update.
- Once exported, a workout is not uploaded again. Source edits are reported as `changed`; this version does not update or delete existing Strava activities. Source deletion also leaves the exported activity intact. Strava activity visibility follows your Strava account settings.
- Pending upload IDs are persisted and polled after restart. A timeout, server error, or crash while uploading leaves the session `uncertain`; it is **not automatically submitted again**. An external ID is a correlation key, not a guarantee of server-side idempotency.
- To recover an uncertain upload, open the activity on Strava and take its numeric ID from the activity URL. Run `reconcile-activity SESSION_UUID ACTIVITY_ID`. Alternatively, use `reconcile SESSION_UUID UPLOAD_ID` if the upload ID is known. Both verify the external ID before attaching the result. Only if no activity/upload exists, run `retry SESSION_UUID --confirm-no-activity` and then `sync`. Failed uploads also need this explicit retry after correction; do not retry while a Strava job is still processing.
- An explicit retry retains the session identity and previous attempt history, but uses a fresh `.retryN.json` file identifier because Strava caches failed jobs by external ID. For known upload IDs, retry verifies the remote failure and refuses successful or still-processing jobs. Source data and mappings are revalidated before sending the new attempt.
- Rate limits persist a cooldown; daily exhaustion waits for the next UTC day. A rejected 429 is retried in a later cycle. A failed/uncertain OAuth refresh may require authorization again. Commands redact API response bodies and secrets from errors.

Strava accounts authorize their own registered application. New applications have limited athlete capacity; see [Strava's rate limits and athlete capacity](https://developers.strava.com/docs/rate-limits/). Use HTTPS for remote services and follow [Strava's authentication documentation](https://developers.strava.com/docs/authentication/).

## Export states

| State | Meaning | Action |
| --- | --- | --- |
| `ready` | Valid source workout with complete mappings | Run `sync` or the watcher. |
| `blocked` | Missing mappings or unsupported set data | Inspect `missing` and `problems` in `preview`. |
| `processing` | Strava has accepted a job | Let a later sync poll it. |
| `exported` | Activity ID is journaled | Keep state for duplicate prevention. |
| `changed` | Source differs from its exported fingerprint | Review manually; remote activities are not updated. |
| `uncertain` | A write may have committed without a usable response | Inspect Strava and reconcile. |
| `failed` | Upload was rejected | Correct the cause before explicit retry. |
| `retry` | An explicit retry was approved | A later sync revalidates and submits a fresh file ID. |
