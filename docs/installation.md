# Installation

## Requirements

Docker Engine or Docker Desktop with Compose v2 supports the released Linux amd64 and arm64 images. Source installation requires Python 3.12 or later. wger must expose timestamped sessions and session-linked logs. Older date/time-only session APIs are unsupported.

## Install methods

=== "Released container"

    Download `docker-compose.yml` and `env.example` from [v0.3.0](https://github.com/willtheorangeguy/wger-strava-connector/releases/tag/v0.3.0). Rename `env.example` to `.env`, configure credentials, then pull:

    ```sh
    docker compose pull
    docker compose run --rm connector --help
    ```

=== "Source container"

    ```sh
    git clone https://github.com/willtheorangeguy/wger-strava-connector.git
    cd wger-strava-connector
    cp .env.example .env
    docker compose -f compose.build.yaml build
    docker compose -f compose.build.yaml run --rm connector --help
    ```

    Use `-f compose.build.yaml` for subsequent commands. It shares the standalone project and state volume. Stop the other deployment first.

=== "Python development"

    ```sh
    python -m venv .venv
    . .venv/bin/activate
    pip install -r requirements.lock
    pip install --no-deps -e .
    wger-strava --help
    ```

    Set environment variables explicitly. The Python entry point does not load `.env` and defaults `DATA_DIR` to `/data`; use a writable local directory such as `./runtime`.

## Verify the installation

`--help` prints the available subcommands without opening state or contacting an API. Complete [getting started](getting-started.md) for an authenticated `check` and `preview`.

## Upgrading

Change `CONNECTOR_VERSION` to the release version without `v`, then run `docker compose pull` and `docker compose up -d`. Keep the state volume. Upgrade the media image to the matching version when enabled.

## Uninstalling

`docker compose down` removes the connector containers and network but preserves named volumes. Keep the state and browser volumes for recovery or reinstalling. Deleting state removes duplicate prevention and OAuth credentials.
