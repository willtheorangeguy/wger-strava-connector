# Known Issues — wger-strava-connector

Concrete defects and gaps found while writing this repository's documentation.
**Nothing here was changed** — each one needs a code, configuration, or
licensing decision rather than a documentation one.

Ordered by severity. See [`docs/roadmap.md`](../roadmap.md) for the narrative version,
which also covers deliberate non-goals.

**2 open:** 2 medium.

## 1. Historical design notes misstate the carrier artwork license

**Severity:** Medium
**Where:** `design/README.md:24–26`; `src/wger_strava/media/assets/carrier-LICENSE.txt`

**What:** The design notes describe every comparison illustration as original MIT artwork, while the carrier attribution identifies an adapted CC BY-SA 4.0 silhouette by TheFrenchKing.

**Why it matters:** Readers reusing the artwork from those notes can miss the separate attribution and share-alike notice.

**Suggested fix:** Update the historical design notes to distinguish the carrier exception and link its existing attribution notice; preserve both license texts.

## 2. Current setup defaults target an unpublished release

**Severity:** Medium
**Where:** `docker-compose.yml`; `.env.example`; GitHub Releases checked 2026-10-22

**What:** The current checkout defaults to image version 0.3.0, and the prior README directs readers to release v0.3.0. GitHub exposes no such release/tag; the latest published release at the check was v0.2.1.

**Why it matters:** Following the advertised release-download setup does not provide the matching current setup files. The new docs use the verified source build path and identify the published-version boundary.

**Suggested fix:** Publish the version only after the repository release gates pass, or keep default download/image instructions aligned with the latest published version until then. Do not create a release as part of a documentation-only pass.
