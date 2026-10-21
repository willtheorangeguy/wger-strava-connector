# Live browser feasibility

Verified on October 20, 2026 using Docker Desktop Linux containers, Chromium and one consenting account owner's nominated private Strava activity. Account identifiers, the activity URL, browser state, test journals and screenshots are private local artifacts, excluded from Git.

## Confirmed

- The owner signed in interactively through the temporary noVNC viewer. Explicit session-cookie save/restore allowed the authenticated browser to restart headlessly.
- The nominated activity exposed edit controls for the signed-in athlete. Its visibility was Only You.
- The editor accepted both generated dark PNG cards in a single native file selection. Both previews loaded before Save was clicked. No activity input fields were changed before saving.
- After Save, both cards appeared on the activity page. A further fresh browser session loaded two distinct persisted media thumbnails. Visual inspection confirmed the summary and comparison artwork, and Only You visibility was retained.
- Upload intent was journaled before file selection. Subsequent verification used reads only and did not reselect or reupload either file.

These were synthetic workout cards attached to an existing activity for feasibility testing. This was not a test of automatic generation from that activity or of a new wger export.

## Live UI details for implementation

- An empty editor offers **Drag and drop media**. Clicking it opens a native multiple-file chooser; the file input may not exist until this interaction.
- The empty prompt disappears after images are attached. Reopening an editor with photos must not wait for that prompt to appear.
- The selected previews initially use the original filenames as image alt text, but Strava removes those alt values after Save. Filenames cannot be the durable verification key.
- The observed editor used thumbnail images with a `Thumbnail--thumbnail-image` class prefix. This is an implementation detail that may change; future verification should capture stable media identities and handle processing delays.
- The first post-save check stopped on the missing empty-state prompt. Read-only recovery in a fresh browser verified the saved photos. No second upload was attempted.

The normal mock upload helper remains restricted to mock origins. This operator-run proof establishes browser-upload feasibility for one account; the production media worker, durable outbox, media identity verification and automatic integration with completed wger exports remain to be implemented. No new release was published for this proof.
