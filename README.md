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

Download `docker-compose.yml` and `env.example` from [v0.3.0](https://github.com/willtheorangeguy/wger-strava-connector/releases/tag/v0.3.0). Rename `env.example` to `.env` and set your wger token, Strava application credentials and timezone. Docker Compose pulls the published image.

```sh
docker compose pull
docker compose run --rm connector auth-url
docker compose run --rm -i connector auth-complete
```

Open the consent URL, then paste the full localhost callback address into `auth-complete`. See [getting started](docs/getting-started.md).

## Usage

```sh
docker compose run --rm connector preview
docker compose run --rm connector exercises
docker compose run --rm connector map 123 BARBELL_BENCH_PRESS
docker compose run --rm connector sync
docker compose up -d
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

Open a [GitHub Discussion](https://github.com/willtheorangeguy/wger-strava-connector/discussions/new) or file an [issue](https://github.com/willtheorangeguy/wger-strava-connector/issues/new/choose).

## Contributing

Contributions welcome. See the org-wide [Contributing Guide](https://github.com/willtheorangeguy/.github/blob/main/CONTRIBUTING.md) and [Code of Conduct](https://github.com/willtheorangeguy/.github/blob/main/CODE_OF_CONDUCT.md).

## License

MIT — see [`LICENSE`](LICENSE).
