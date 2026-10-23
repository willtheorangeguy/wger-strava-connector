# wger → Strava connector

Export completed wger strength workouts as structured Strava `WeightTraining` activities. Run this Docker companion for one wger account and one Strava athlete. Optional browser workers attach summary and comparison cards after confirmed exports.

## Key features

- Export actual exercises, repetitions, loads and timed sets.
- Hold whole workouts when mappings or source data are incomplete.
- Persist OAuth, account bindings, asynchronous jobs and recovery history.
- Run continuously beside wger with an optional independent image worker.

## Quick start

Build the current source checkout and configure `.env` as described in [getting started](getting-started.md), then authorize and inspect your first workouts:

```sh
docker compose -f compose.build.yaml build
docker compose -f compose.build.yaml run --rm connector auth-url
docker compose -f compose.build.yaml run --rm -i connector auth-complete
docker compose -f compose.build.yaml run --rm connector preview
```

Follow [getting started](getting-started.md) for prerequisites, exercise approvals and the first export.

## Where to next

<div class="grid cards" markdown>

- [Installation](installation.md): released images, source builds and upgrades.
- [Configuration](configuration.md): environment defaults and credentials.
- [Usage](usage.md): state meanings, conversion and recovery.
- [Workout images](media.md): worker setup, login and receipts.
- [Architecture](architecture.md): API, journal and queue boundaries.
- [Testing](testing.md): real-wger fixtures and mock Strava checks.

</div>

## Support

Open an [issue](https://github.com/willtheorangeguy/wger-strava-connector/issues/new/choose). Follow the org-wide [contributing guide](https://github.com/willtheorangeguy/.github/blob/main/CONTRIBUTING.md).
