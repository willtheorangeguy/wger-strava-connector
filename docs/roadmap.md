# Roadmap

Current boundaries come from the implemented export and recovery behavior. They are limitations, not scheduled releases.

- Legacy wger sessions without timestamps and session-linked logs are unsupported.
- The exercise catalog is a snapshot of 656 supported Strava identifiers checked on 2026-10-20. Unlisted exercises need a supported equivalent or a catalog update.
- Source edits and deletions do not update or delete already exported Strava activities.
- Supersets, RIR, rest targets and individual notes have no structured destination field in this upload path.
- Old exports do not automatically receive image jobs. Browser automation depends on the live site and a valid saved session.
- Muscle diagrams use available source metadata. Unrecognized names and unavailable exercise metadata are retained in the job for inspection.

Review an affected workout with `docker compose -f compose.build.yaml run --rm connector preview` while the watcher is stopped. See [usage](usage.md) for recovery and [workout images](media.md) for image behavior.
