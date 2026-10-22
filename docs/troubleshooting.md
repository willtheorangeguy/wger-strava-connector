# Troubleshooting

## Another connector command is using this state volume

Stop the watcher before maintenance and restart it afterwards:

```sh
docker compose stop connector
docker compose run --rm connector status
docker compose up -d
```

## Authorization state is missing, expired or does not match

Run `auth-url` again and complete its callback within 15 minutes, using the same state volume. A browser connection error on the localhost callback page is expected: paste the full address into `auth-complete`. Grant all requested scopes.

## Account or API endpoint changed

Restore the original account/URL settings. The journal refuses to mix source usernames, source origins, Strava applications or athletes. Use a separate state volume for another pair of accounts.

## Preview reports blocked or no workouts

Inspect `missing` and `problems`. Approve supported mappings and correct invalid source sets. Check the saved UTC date boundary, completion timestamp, settling delay and wger version. Unfinished and future sessions are excluded.

## Upload is processing, failed or uncertain

Let `processing` jobs poll on a later sync. For an uncertain outcome, inspect Strava and recover with the matching upload/activity ID. Only explicitly retry after verifying no successful activity exists. See [usage](usage.md) and [the command reference](api.md).

## HTTP 429 or uncertain refresh

Wait for the persisted cooldown. Daily exhaustion waits until the next UTC day. Reauthorize when the connector reports an uncertain OAuth refresh. API errors deliberately omit remote response bodies.

## Browser profile is busy or images remain pending

Stop the media worker before login, complete login as the same athlete, then restart it. Confirm `CONNECTOR_STATE_VOLUME` names the core volume. Inspect `/data/media/errors` and receipts for held work. Never delete a receipt to force another upload. Missing metadata leaves regions unhighlighted without blocking the activity export.
