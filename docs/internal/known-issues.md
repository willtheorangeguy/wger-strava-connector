# Known Issues — wger-strava-connector

Concrete defects and gaps found while writing this repository's documentation.
**Nothing here was changed** — each one needs a code, configuration, or
licensing decision rather than a documentation one.

Ordered by severity. See [`docs/roadmap.md`](../roadmap.md) for the narrative version,
which also covers deliberate non-goals.

**1 open:** 1 medium.

## 1. Historical design notes misstate the carrier artwork license

**Severity:** Medium
**Where:** `design/README.md:24–26`; `src/wger_strava/media/assets/carrier-LICENSE.txt`

**What:** The design notes describe every comparison illustration as original MIT artwork, while the carrier attribution identifies an adapted CC BY-SA 4.0 silhouette by TheFrenchKing.

**Why it matters:** Readers reusing the artwork from those notes can miss the separate attribution and share-alike notice.

**Suggested fix:** Update the historical design notes to distinguish the carrier exception and link its existing attribution notice; preserve both license texts.
