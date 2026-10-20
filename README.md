# strava-grokbot-bridge

Read-only [Strava](https://www.strava.com/) MCP for **GrokBot**. Each user runs
this on **their own GrokBot cloud computer**. The Bot starts it as a **stdio
command**. There is no public host, no ngrok, and no marketplace tile.

Fork of [eddmann/strava-mcp](https://github.com/eddmann/strava-mcp) (MIT,
© 2025 Edd Mann), pinned at
[`2c6fa6991ffa2c4a443887728aaf8eaab5829cea`](https://github.com/eddmann/strava-mcp/commit/2c6fa6991ffa2c4a443887728aaf8eaab5829cea).
See [UPSTREAM.md](UPSTREAM.md).

**Compatible with Strava.** This project is not affiliated with, endorsed by,
or sponsored by Strava, Inc. Do not name your API app anything that implies an
official Strava product (use something like “GrokBot Activity Bridge”). When
you link an activity, say “View on Strava”.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

**Install and attach:** follow **[INSTALL.md](INSTALL.md)** (clone or `uvx` on
the GrokBot cloud computer, put client id/secret on the computer, `strava-mcp
auth --stdio` with Take over, then add a custom stdio **command** in chat).

## What GrokBot users do

Do **not** use GrokBot’s Add-connector / Plugins marketplace. That catalog is
Gmail, Notion, and similar tiles. Strava is not there, and this fork is not a
URL connector.

Do **not** paste Strava access tokens, refresh tokens, or client secrets into
chat.

### 1. Create your own Strava API app

1. Open [strava.com/settings/api](https://www.strava.com/settings/api)
2. Create an application (this currently requires a Strava subscription)
3. Authorization Callback Domain: `localhost`
4. Website can be `http://localhost`
5. Keep the client id and secret on the computer — not in chat

New apps start in single-player mode (only you can authorize). That is enough
if you own the app.

### 2. Install on the GrokBot computer

Ask the Bot to clone this repo onto the computer:

```bash
git clone https://github.com/naoiseirwin/strava-grokbot-bridge.git /workspace/strava-grokbot-bridge
```

Requires [uv](https://github.com/astral-sh/uv).

### 3. Authorize on the computer (Take over)

Put `STRAVA_CLIENT_ID` and `STRAVA_CLIENT_SECRET` on the computer with a GrokBot
secret-request, or write them into `/workspace/.strava-mcp.env`. Then:

```bash
uv run --directory /workspace/strava-grokbot-bridge strava-mcp auth --stdio
```

A browser on **this computer** opens Strava’s consent screen. If you need a
password, passkey, or 2FA, use **Take over**. Do not paste the redirect URL
into chat.

Tokens are stored at `/workspace/.strava-mcp.env` (mode `600`). Access tokens
last about six hours; the server refreshes them. All Bots on your Cursor
account share this computer, so they can all read that file.

Scopes (read-only): `profile:read_all`, `activity:read_all`, `activity:read`.

### 4. Attach the stdio command

In GrokBot chat, send:

> Add a custom MCP server called strava that runs: `uv run --directory /workspace/strava-grokbot-bridge strava-mcp`

The Bot should repeat the name, command, and args. Click **Add it**.

`uvx` form (same computer, no checkout required after git is public):

> Add a custom MCP server called strava that runs: `uvx --from git+https://github.com/naoiseirwin/strava-grokbot-bridge strava-mcp`

### 5. Use it

Type `@` and attach `strava`. Then:

- “What’s my athlete profile?”
- “Show my runs from the last 30 days”

Those call `get_athlete_profile` and `query_activities`.

GrokBot skill the Bot can follow: [skills/grokbot-strava/SKILL.md](skills/grokbot-strava/SKILL.md).

## Tools

| Tool | Description |
| --- | --- |
| `query_activities` | Query activities with filters and optional laps/zones/streams |
| `get_activity_social` | Comments and kudos |
| `get_athlete_profile` | Profile, optional stats and zones |
| `query_segments` | Segment by id, starred list, or explore bounds |
| `get_segment_leaderboard` | Segment leaderboard |
| `query_routes` | Route by id or list |
| `export_route` | Export GPX/TCX |
| `analyze_training` | Training summary over a period |
| `compare_activities` | Side-by-side compare |
| `find_similar_activities` | Similar efforts |

`star_segment` is not registered. This fork does not request `profile:write`.

Resource: `strava://athlete/profile`. Prompts: `analyze_recent_training`,
`segment_performance`, `activity_deep_dive`, `compare_recent_runs`,
`training_summary`, `race_performance_analysis`.

## Token file

| Place | Path |
| --- | --- |
| GrokBot computer (default) | `/workspace/.strava-mcp.env` |
| Override | `STRAVA_MCP_ENV_FILE` |
| Desktop fallback | `~/.strava-mcp.env` |
| Local checkout if `.env` exists | `./.env` |

See [SECURITY.md](SECURITY.md) to revoke (Strava → Settings → My Apps).

## Not the product

HTTP / Streamable HTTP, Lambda, DynamoDB, Docker, and ngrok remain in the tree
because they came from upstream. They are **not** how GrokBot users attach this
server. Cursor’s connector backend cannot reach `localhost` on your laptop, and
this project does not stand up a public URL.

Do not `uvx mcp-strava` from PyPI — that is upstream, not this fork.

## Development

```bash
uv sync --extra http
make test
make lint
```

Tests are mocked. They do not call the live Strava API.

## License

MIT. Copyright (c) 2025 Edd Mann. Fork modifications Copyright (c) 2026
Naoise Irwin. See [LICENSE](LICENSE).
