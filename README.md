<!-- Logo -->
<h1 align="center">wger → Strava connector</h1>
<!-- Tagline -->
<h4 align="center">Export completed wger strength workouts to Strava with structured sets and optional image cards.</h4>
<!-- Badges -->
<div align="center">
<img alt="Issues" src="https://img.shields.io/github/issues/willtheorangeguy/wger-strava-connector">
<img alt="Pull requests" src="https://img.shields.io/github/issues-pr/willtheorangeguy/wger-strava-connector">
<img alt="License" src="https://img.shields.io/github/license/willtheorangeguy/wger-strava-connector">
<img alt="docs-lint workflow" src="https://github.com/willtheorangeguy/wger-strava-connector/actions/workflows/docs-lint.yml/badge.svg">
<img alt="docs workflow" src="https://github.com/willtheorangeguy/wger-strava-connector/actions/workflows/docs.yml/badge.svg">
<img alt="media workflow" src="https://github.com/willtheorangeguy/wger-strava-connector/actions/workflows/media.yml/badge.svg">
<img alt="publish workflow" src="https://github.com/willtheorangeguy/wger-strava-connector/actions/workflows/publish.yml/badge.svg">
<img alt="test workflow" src="https://github.com/willtheorangeguy/wger-strava-connector/actions/workflows/test.yml/badge.svg">
</div>
<!-- Nav -->
<p align="center"><a href="#key-features">Key Features</a> • <a href="#installation">Installation</a> • <a href="#usage">Usage</a> • <a href="#documentation">Documentation</a> • <a href="#support">Support</a> • <a href="#license">License</a></p>

## Key Features

- Export actual exercises, sets, repetitions, weights and timed holds.
- Require explicit exercise mappings and hold incomplete workouts for review.
- Preserve account bindings, OAuth tokens and upload state in a durable journal.
- Recover asynchronous or uncertain uploads without automatic resubmission.
- Attach optional summary and comparison cards with an independent browser worker.

## Installation

Current source version `0.3.0` was not yet published as a release on 2026-10-22. Build the checkout for the features documented here. See [installation](docs/installation.md) for the published version.

```sh
git clone https://github.com/willtheorangeguy/wger-strava-connector.git
cd wger-strava-connector
cp .env.example .env
# Fill in the source API key/token, Strava app credentials and timezone.
docker compose -f compose.build.yaml build
docker compose -f compose.build.yaml run --rm connector auth-url
docker compose -f compose.build.yaml run --rm -i connector auth-complete
```

Open the consent URL and paste the complete localhost callback into the prompt. Follow [getting started](docs/getting-started.md) for account setup.

## Usage

```sh
docker compose -f compose.build.yaml run --rm connector preview
docker compose -f compose.build.yaml run --rm connector exercises
docker compose -f compose.build.yaml run --rm connector map 123 BARBELL_BENCH_PRESS
docker compose -f compose.build.yaml run --rm connector sync
docker compose -f compose.build.yaml up -d
```

Replace `123` with a missing wger exercise ID from `preview`. The watcher runs every 15 minutes by default. Stop it before stateful maintenance. Keep the state volume to prevent duplicate exports. Requires timestamped wger sessions; tested with wger `2.8.0-dev.1`.

## Documentation

Read the [documentation site](https://williamvdg.me/wger-strava-connector/) or browse [`docs/`](docs/index.md):
[Getting started](docs/getting-started.md) · [Installation](docs/installation.md) · [Usage](docs/usage.md) · [Configuration](docs/configuration.md) · [Troubleshooting](docs/troubleshooting.md).

## Automatic workout images

Version 0.3.0 includes optional automatic cards. Follow [workout images](docs/media.md) for the matching media container, browser login and recovery.

## Experimental workout image tools

Historical prototype notes remain in [design/](design/README.md). Current setup is in [workout images](docs/media.md).

## Support

Open an [issue](https://github.com/willtheorangeguy/wger-strava-connector/issues/new/choose).

## Contributing

Contributions welcome. See the org-wide [Contributing Guide](https://github.com/willtheorangeguy/.github/blob/main/CONTRIBUTING.md) and [Code of Conduct](https://github.com/willtheorangeguy/.github/blob/main/CODE_OF_CONDUCT.md).

## License

MIT — see [`LICENSE`](LICENSE).
