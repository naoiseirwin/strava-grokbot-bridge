---
name: grokbot-strava
description: >-
  Attach this user's Strava account to GrokBot via a stdio MCP command on the
  cloud computer. Use when the user wants Strava activities, athlete profile,
  segments, or routes in GrokBot. Do not use the Add-connector marketplace.
  Never ask for Strava tokens in chat. Do not register a Strava API app for them.
---

# GrokBot Strava bridge

This repo is a read-only fork of [eddmann/strava-mcp](https://github.com/eddmann/strava-mcp).
The product is a **stdio command GrokBot starts on the cloud computer**. It is
not a marketplace connector and not a public HTTPS host.

Compatible with Strava. Not affiliated with Strava.

## Hard rules

- Do **not** open Add-connector / Plugins marketplace. Strava is not a tile there.
- Do **not** add a public URL, ngrok tunnel, or Lambda URL.
- Do **not** ask for an access token, refresh token, or client secret in chat.
- Do **not** register a Strava API application on the user's behalf.
- Client id/secret: GrokBot secret-request, or env on the MCP server entry, or
  a mode-`600` file on the computer. Never the transcript.
- For Strava login, passkey, or 2FA, tell the user to **Take over** the computer
  browser. They must not paste passwords into chat.

## What the Bot should do

1. Confirm the user already has (or will create) **their own** Strava API app at
   [strava.com/settings/api](https://www.strava.com/settings/api). Callback
   domain: `localhost`. Display name must not imply an official Strava product
   (example: "GrokBot Activity Bridge"). Creating an app currently needs a
   Strava subscription. Single-player is enough for the owner.
2. Clone this package onto the computer if it is not already there:

   ```bash
   git clone https://github.com/naoiseirwin/strava-grokbot-bridge.git /workspace/strava-grokbot-bridge
   ```

3. Put `STRAVA_CLIENT_ID` and `STRAVA_CLIENT_SECRET` on the computer (secret-request
   or `/workspace/.strava-mcp.env`). Then run:

   ```bash
   uv run --directory /workspace/strava-grokbot-bridge strava-mcp auth --stdio
   ```

   A browser on **this computer** opens. Tell the user to Take over if Strava
   asks for a password, passkey, or 2FA. Tokens land in `/workspace/.strava-mcp.env`
   (mode 600). Do not print token values.

4. Ask the user to send this chat message (or send it yourself as the add
   request and wait for their confirmation):

   > Add a custom MCP server called strava that runs: `uv run --directory /workspace/strava-grokbot-bridge strava-mcp`

   Alternative once they prefer `uvx` from git:

   > Add a custom MCP server called strava that runs: `uvx --from git+https://github.com/naoiseirwin/strava-grokbot-bridge strava-mcp`

5. Repeat the **name**, **command**, and **args**. Wait for them to click Add it.
   Do not also install a catalog plugin named Strava.
6. After the Bot reports tools, tell them to type `@` and attach `strava`.
   Smoke: `get_athlete_profile`, then `query_activities` for recent runs.

## Attach details

| Field | Value |
| --- | --- |
| Name | `strava` |
| Transport | stdio command on the GrokBot computer |
| Command (checkout) | `uv` `run` `--directory` `/workspace/strava-grokbot-bridge` `strava-mcp` |
| Command (uvx) | `uvx` `--from` `git+https://github.com/naoiseirwin/strava-grokbot-bridge` `strava-mcp` |
| Token file | `/workspace/.strava-mcp.env` |
| Scopes | `profile:read_all,activity:read_all,activity:read` |

If the server needs client id/secret as env on the **server entry**, name the
variables `STRAVA_CLIENT_ID` and `STRAVA_CLIENT_SECRET` and collect them with a
secret-request. The stdio process still reads `/workspace/.strava-mcp.env` for
tokens.

## Shared computer

All Bots on this Cursor account share the computer. The token file is visible
to every Bot the user runs. Say that once.

## Tools you can call after attach

Read-only: `query_activities`, `get_activity_social`, `get_athlete_profile`,
`query_segments`, `get_segment_leaderboard`, `query_routes`, `export_route`,
`analyze_training`, `compare_activities`, `find_similar_activities`.

There is no `star_segment`. Do not request `profile:write`.

When linking an activity, use "View on Strava".
