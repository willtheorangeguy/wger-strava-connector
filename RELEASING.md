# Release preparation

This connector is currently a local Git repository. Before publishing a release, create its GitHub repository, push `main`, and dispatch the test workflow to exercise the public wger harness. No production Strava credentials are needed for tests.

1. Update `pyproject.toml` and `src/wger_strava/__init__.py` to the same version. Update the changelog and validation notes.
2. Run `python test_harness.py`, validate Compose examples, and inspect `git diff --check`.
3. Create and push an annotated `vMAJOR.MINOR.PATCH` tag. Publish the corresponding GitHub release. A tag push alone does not publish a container.
4. `.github/workflows/publish.yml` validates the version, gates publication on tests, then builds GHCR images for Linux amd64 and arm64 with provenance and an SBOM. It uses `GITHUB_TOKEN` and needs Packages write permission.
5. Stable releases receive the full version, minor version, and `latest` tags. Prereleases receive only their complete version; GitHub's prerelease flag must match the version suffix. Set package visibility to public if needed and verify an anonymous pull.

The default Compose file builds from the checkout. To use a future published image, replace `build: .` and the local `image:` with `image: ghcr.io/OWNER/wger-strava-connector:VERSION` in your deployment. The existing-wger overlay can be changed the same way. Never put real tokens or `.env` in a release.
