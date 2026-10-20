# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-10-20

### Changed

- Re-home as `strava-grokbot-bridge`, a GrokBot cloud-computer stdio fork of eddmann/strava-mcp (pinned at `2c6fa6991ffa2c4a443887728aaf8eaab5829cea`)
- Default OAuth scopes are read-only (`profile:read_all`, `activity:read_all`, `activity:read`); `star_segment` is not registered
- Persist stdio tokens at `/workspace/.strava-mcp.env` on a GrokBot computer (mode 600)
- Auth wizard opens the computer browser, listens on localhost, and tells the user to Take over for login/2FA

### Added

- GrokBot skill at `skills/grokbot-strava/SKILL.md`
- `SECURITY.md` and `UPSTREAM.md`

[1.1.0]: https://github.com/naoiseirwin/strava-grokbot-bridge/releases/tag/v1.1.0

## [1.0.0] - 2026-05-20

### Added

- Initial Strava MCP server release
- Strava activity, athlete, segment, route, and analysis tools
- MCP resource for athlete profile context
- MCP prompts for training analysis, segment performance, activity analysis, run comparison, training summary, and race performance
- `strava-mcp` server entrypoint with stdio and HTTP transport modes
- `strava-mcp auth` interactive OAuth setup with token persistence
- Docker image support via GitHub Container Registry
- AWS Lambda and CDK deployment support for HTTP mode

[1.0.0]: https://github.com/eddmann/strava-mcp/releases/tag/v1.0.0
