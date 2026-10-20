# Install strava-grokbot-bridge for GrokBot

This fork is a **read-only Strava MCP**. Each person runs it on **their own
GrokBot cloud computer**. GrokBot starts it as a **stdio command**. There is no
public host, no ngrok, and no marketplace tile.

**Compatible with Strava.** This project is not affiliated with, endorsed by,
or sponsored by Strava, Inc. When you link an activity, say “View on Strava”.

Repo: [github.com/naoiseirwin/strava-grokbot-bridge](https://github.com/naoiseirwin/strava-grokbot-bridge).
Fork of [eddmann/strava-mcp](https://github.com/eddmann/strava-mcp).

## 1. Prerequisites

You need all of these before GrokBot can see your activities.

### Your own Strava API app

1. A **Strava subscription**. Creating an API application currently requires one.
2. Open [strava.com/settings/api](https://www.strava.com/settings/api) and
   create an application **you own**. Each GrokBot user creates their own app
   and authorizes their own athlete. No shared personal token.
3. **Authorization Callback Domain:** `localhost` (that hostname, not a full
   URL). Strava already allows this. Website can be `http://localhost`.
4. **App display name** must not imply an official Strava product. Use something
   like **GrokBot Activity Bridge**. Do not name it “Strava …” or anything that
   reads as Strava’s own app.
5. New apps start in **single-player** mode (only you can authorize). That is
   enough if you own the app.

Do not copy the access token or refresh token from the API settings page.
Those tokens are `read` only and are not how this server authenticates. This
repo will not register a Strava API app for you.

Keep the **client id** and **client secret** off chat. You put them on the
computer in step 3.

### On the GrokBot computer

- A GrokBot cloud computer (the Bot runs commands there; files persist for
  your Cursor account).
- [uv](https://github.com/astral-sh/uv) (Python 3.11+).

## 2. Clone or uvx on the GrokBot computer

Install **on the GrokBot cloud computer**, not on your laptop. Ask the Bot to
run one of the following. Checkout path, when you clone:

`/workspace/strava-grokbot-bridge`

### Clone, then `uv run`

```bash
git clone https://github.com/naoiseirwin/strava-grokbot-bridge.git /workspace/strava-grokbot-bridge
```

Requires [uv](https://github.com/astral-sh/uv). Later steps use
`uv run --directory /workspace/strava-grokbot-bridge …`.

### `uvx` from git (no checkout)

You can skip the clone and run the CLI from this GitHub repo. Tokens still
live on this computer. Package name: `strava-grokbot-bridge`. CLI: `strava-mcp`.

Do **not** `uvx mcp-strava` from PyPI — that is upstream, not this fork.

## 3. Put client id and secret on the computer

Never paste `STRAVA_CLIENT_ID`, `STRAVA_CLIENT_SECRET`, access tokens, or
refresh tokens into GrokBot chat.

Do one of these on the computer:

- A GrokBot **secret-request**, if the Bot offers one, written onto the
  computer (not into the transcript).
- Write the two values into `/workspace/.strava-mcp.env` (mode `600`). Shape:

  ```
  STRAVA_CLIENT_ID=your_client_id_here
  STRAVA_CLIENT_SECRET=your_client_secret_here
  ```

  The repo’s `.env.example` is the same two keys. If you create the file by
  hand: `chmod 600 /workspace/.strava-mcp.env`.
- Or set `STRAVA_CLIENT_ID` and `STRAVA_CLIENT_SECRET` as env on the **stdio
  MCP server entry** (still not in chat). The process also reads
  `/workspace/.strava-mcp.env` for tokens after you authorize.

## 4. Authorize: `strava-mcp auth --stdio`

From a clone:

```bash
uv run --directory /workspace/strava-grokbot-bridge strava-mcp auth --stdio
```

Without a clone (`uvx`):

```bash
uvx --from git+https://github.com/naoiseirwin/strava-grokbot-bridge strava-mcp auth --stdio
```

What happens:

- A browser **on this computer** opens Strava’s consent screen.
- The wizard listens on `http://127.0.0.1:18741/callback` for five minutes.
- If Strava asks for a password, passkey, or 2FA, use **Take over** on that
  browser. Do not paste the redirect URL, password, or codes into chat.
- Tokens land in `/workspace/.strava-mcp.env` (mode `600`). If `/workspace`
  is not a directory, the fallback is `~/.strava-mcp.env`. Override with
  `STRAVA_MCP_ENV_FILE`.
- Access tokens last about six hours; the server refreshes them. Strava
  rotates the refresh token; the file is overwritten.
- Scopes (read-only): `profile:read_all`, `activity:read_all`,
  `activity:read`. This fork does not request `profile:write`.

All GrokBots on your Cursor account share this computer, so they can all
read that file. Isolation is between Cursor users, not between your Bots.

## 5. Add the custom MCP command in GrokBot chat

Do **not** open Add-connector / Plugins. In GrokBot chat, send one of these.

Checkout (`uv run`):

> Add a custom MCP server called strava that runs: `uv run --directory /workspace/strava-grokbot-bridge strava-mcp`

`uvx` (same computer, no checkout required):

> Add a custom MCP server called strava that runs: `uvx --from git+https://github.com/naoiseirwin/strava-grokbot-bridge strava-mcp`

The Bot should repeat the **name**, **command**, and **args**. Click **Add it**.
Do not also install a catalog plugin named Strava.

| Field | Value |
| --- | --- |
| Name | `strava` |
| Transport | stdio command on the GrokBot computer |
| Command (checkout) | `uv run --directory /workspace/strava-grokbot-bridge strava-mcp` |
| Command (uvx) | `uvx --from git+https://github.com/naoiseirwin/strava-grokbot-bridge strava-mcp` |

## 6. Attach with `@` and ask

Type `@` and attach `strava`. Then:

- “What’s my athlete profile?”
- “Show my runs from the last 30 days”

Those call `get_athlete_profile` and `query_activities`.

Other read tools: `get_activity_social`, `query_segments`,
`get_segment_leaderboard`, `query_routes`, `export_route`, `analyze_training`,
`compare_activities`, `find_similar_activities`. There is no `star_segment`.

## 7. What not to do

- Do **not** use GrokBot’s **Add-connector** / Plugins marketplace catalog.
  That catalog is Gmail, Notion, and similar tiles. Strava is not there, and
  this fork is not a URL connector.
- Do **not** paste client secrets, access tokens, or refresh tokens into chat.
- Do **not** `uvx mcp-strava` from PyPI. That package is upstream, not this
  fork.
- Do **not** add a **localhost** (or laptop) URL as a connector. Cursor’s
  connector backend fetches public HTTPS from the open internet and rejects
  `localhost` / `127.0.0.1` / private IPs. This project does not stand up a
  public URL.
- Do **not** put this in Cursor `mcp.json` and expect GrokBot to pick it up.
  Attach by asking GrokBot in chat to add the stdio **command**.
- Do **not** name your API app as if it were an official Strava product.

HTTP / Streamable HTTP, Lambda, DynamoDB, Docker, and ngrok remain in the
tree because they came from upstream. They are **not** how GrokBot users
attach this server.

## 8. Revoke / uninstall

1. Strava → [Settings → My Apps](https://www.strava.com/settings/apps) →
   revoke the application you created.
2. Delete the env file on the computer: `/workspace/.strava-mcp.env` (or
   the path in `STRAVA_MCP_ENV_FILE`).
3. Remove the custom MCP server named `strava` from GrokBot if you added one.
4. Optional: delete the checkout `/workspace/strava-grokbot-bridge`.

Details: [SECURITY.md](SECURITY.md).

## See also

- [README.md](README.md) — tools, token-file table, development
- [skills/grokbot-strava/SKILL.md](skills/grokbot-strava/SKILL.md) — same
  install path for the Bot
- [UPSTREAM.md](UPSTREAM.md) — pin; do not install PyPI `mcp-strava`
