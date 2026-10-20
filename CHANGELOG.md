# strava-grokbot-bridge — first public notes

**0.1** · 20 October 2026

What this fork changed versus [eddmann/strava-mcp](https://github.com/eddmann/strava-mcp), pinned at [`2c6fa6991ffa2c4a443887728aaf8eaab5829cea`](https://github.com/eddmann/strava-mcp/commit/2c6fa6991ffa2c4a443887728aaf8eaab5829cea) (upstream v1.0.0 plus later activity-type fixes). Nothing here is a new Strava client.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## Unchanged — tools and client

The Strava API client and the read tools are still eddmann’s. This fork did not rewrite them.

| Tool | What it does |
| --- | --- |
| `query_activities` | Activities, filters, optional laps/zones/streams |
| `get_activity_social` | Comments and kudos |
| `get_athlete_profile` | Profile, optional stats and zones |
| `query_segments` | By id, starred list, or explore bounds |
| `get_segment_leaderboard` | Leaderboard |
| `query_routes` | By id or list |
| `export_route` | GPX/TCX |
| `analyze_training` | Training summary |
| `compare_activities` | Side-by-side |
| `find_similar_activities` | Similar efforts |

Resource `strava://athlete/profile` and prompts `analyze_recent_training`, `segment_performance`, `activity_deep_dive`, `compare_recent_runs`, `training_summary`, and `race_performance_analysis` are unchanged.

HTTP / Streamable HTTP, Lambda, CDK, and Docker stay in the tree. They are not how GrokBot users run this fork.

## Runtime — GrokBot stdio on the cloud computer

This fork is a **stdio command GrokBot starts on the user’s own cloud computer**. There is no public host, no ngrok, and no marketplace connector.

- Package name: `strava-grokbot-bridge` (not PyPI `mcp-strava`)
- CLI: `strava-mcp`
- Attach in GrokBot chat: add a custom MCP server named `strava` that runs `uv run --directory /workspace/strava-grokbot-bridge strava-mcp` (or `uvx --from git+https://github.com/naoiseirwin/strava-grokbot-bridge strava-mcp`)
- Do not `uvx mcp-strava` from PyPI — that is upstream
- The GitHub Actions workflow that published `mcp-strava` to PyPI is removed

## Auth and token path

Each GrokBot user creates **their own** Strava API app and authorizes **their own** athlete. No shared personal token. Do not paste access tokens, refresh tokens, or client secrets into chat.

- Command: `strava-mcp auth --stdio`
- Opens the **computer** browser and listens on `http://127.0.0.1:18741/callback` (5 minutes)
- Password, passkey, or 2FA: **Take over** that browser. Do not paste the redirect URL into chat
- Default token file on a GrokBot computer: `/workspace/.strava-mcp.env` (mode `600`)
- Otherwise: `~/.strava-mcp.env`. Override with `STRAVA_MCP_ENV_FILE`
- Access tokens still last about six hours; the existing refresh path is unchanged
- All Bots on one Cursor account share the computer and can read that file

`.env.example` lists only `STRAVA_CLIENT_ID` and `STRAVA_CLIENT_SECRET`.

## Read-only scopes

Default scopes: `profile:read_all`, `activity:read_all`, `activity:read`.

Upstream also requested `profile:write` for `star_segment`. This fork does not request `profile:write` and does not register `star_segment`.

## Docs and skill

- README leads with GrokBot cloud-computer stdio, not Lambda or ngrok
- [`skills/grokbot-strava/SKILL.md`](https://github.com/naoiseirwin/strava-grokbot-bridge/blob/main/skills/grokbot-strava/SKILL.md) — install and attach path for the Bot
- `SECURITY.md` — what is private, and how to revoke (Strava → Settings → My Apps)
- `UPSTREAM.md` — pin and “do not install PyPI `mcp-strava`”

## License and attribution

MIT. Copyright (c) 2025 Edd Mann. Fork modifications Copyright (c) 2026 Naoise Irwin.

**Compatible with Strava.** Not affiliated with, endorsed by, or sponsored by Strava, Inc. Do not name an API app anything that implies an official Strava product.

## Deliberately not taken

Compared, not forked:

- **[r-huijts/strava-mcp](https://github.com/r-huijts/strava-mcp)** — larger stdio tool set (~25 tools). Extra tools were not imported.
- **[pete-builds/strava-mcp-vault](https://github.com/pete-builds/strava-mcp-vault)** — SQLite cache-aside, long-lived HTTP host, and a connection bearer token. Not imported.

Those remain optional later patches on this fork, not a second implementation.

## Inherited from eddmann 1.0.0 (20 May 2026)

- Initial Strava MCP server: activity, athlete, segment, route, and analysis tools
- MCP resource for athlete profile; analysis prompts
- `strava-mcp` stdio and HTTP transports; `strava-mcp auth`; Docker; AWS Lambda/CDK for HTTP
