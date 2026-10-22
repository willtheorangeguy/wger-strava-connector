# API

The supported interface is the `wger-strava` CLI, also used as the container entry point. Start with `--help`. JSON results go to stdout; handled API/configuration errors go to stderr and exit 1. No HTTP server is exposed.

Stop the watcher before stateful commands. Examples with numeric IDs and UUIDs show the argument format; substitute your own IDs before recovery.

## `auth-url`

Print consent URL and persist a 15-minute nonce.

```sh
docker compose run --rm connector auth-url
```

## `auth-complete`

Read full callback URL from stdin and store OAuth credentials.

```sh
docker compose run --rm -i connector auth-complete
```

## `check`

Verify source username and Strava athlete bindings.

```sh
docker compose run --rm connector check
```

## `preview`

Read eligible sessions, mappings and problems; save initial boundary.

```sh
docker compose run --rm connector preview
```

## `exercises`

Print supported Strava identifiers without opening state.

```sh
docker compose run --rm connector exercises
```

## `map`

Approve an exercise mapping. Replace 123 with an ID reported by preview.

| Argument | Type and constraint |
| --- | --- |
| `exercise` | integer |
| `strava_type` | supported identifier |

```sh
docker compose run --rm connector map 123 BARBELL_BENCH_PRESS
```

## `mappings`

Print approved mappings.

```sh
docker compose run --rm connector mappings
```

## `sync`

Poll pending jobs, then submit ready sessions up to the cycle limit.

```sh
docker compose run --rm connector sync
```

## `watch`

Run sync repeatedly using SYNC_INTERVAL_SECONDS.

```sh
docker compose run --rm connector watch
```

## `status`

Print authorization, athlete, source, exports and cooldown.

```sh
docker compose run --rm connector status
```

## `reconcile`

Verify the remote external ID and attach a known upload.

| Argument | Type and constraint |
| --- | --- |
| `session` | UUID |
| `upload_id` | integer |

```sh
docker compose run --rm connector reconcile 00000000-0000-0000-0000-000000000001 1
```

## `reconcile-activity`

Verify the remote external ID and attach a known activity.

| Argument | Type and constraint |
| --- | --- |
| `session` | UUID |
| `activity_id` | integer |

```sh
docker compose run --rm connector reconcile-activity 00000000-0000-0000-0000-000000000001 1
```

## `retry`

After checking Strava, approve an unresolved failed or uncertain attempt for resubmission.

| Argument | Type and constraint |
| --- | --- |
| `session` | UUID |
| `--confirm-no-activity` | required flag |

```sh
docker compose run --rm connector retry 00000000-0000-0000-0000-000000000001 --confirm-no-activity
```

## External APIs

The connector consumes wger API v2 profile, repetition/weight units, workout sessions, session-filtered logs, day names and optional exercise-info muscle metadata. It uses Strava OAuth and API v3 athlete, uploads and activity lookup endpoints. The upload is multipart JSON with `sport_type=WeightTraining` and UTC `Z` timestamps. Pagination is restricted to the configured origin and HTTP response bodies are redacted from errors.

`check` returns an object containing `wger` (URL and username) and `strava_athlete`. `sync` returns `submitted`, `exports`, `blocked`, and `changed`, or a rate-limited state with `retry_at`. See [usage](usage.md) for state meanings and [the API implementation](https://github.com/willtheorangeguy/wger-strava-connector/blob/HEAD/src/wger_strava/api.py) for request handling.
