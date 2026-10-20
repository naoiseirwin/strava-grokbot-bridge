# Security

This MCP talks to the Strava API with **your** API application and **your**
athlete OAuth tokens. Treat that material as private.

## What is private

- Strava client id and client secret
- Access tokens and refresh tokens
- Activity, route, and profile data returned by the tools

Do not commit `.env`, `.strava-mcp.env`, or `/workspace/.strava-mcp.env`.
Do not paste those values into GrokBot chat. If GrokBot offers a secret-request,
use that for client id/secret. Never send an access or refresh token to the Bot.

## Token file

Default location on a GrokBot cloud computer:

```
/workspace/.strava-mcp.env
```

Override with `STRAVA_MCP_ENV_FILE`. The file is created mode `600`. Access
tokens last about six hours; the server refreshes them and overwrites the
refresh token (Strava rotates it).

Every GrokBot on your Cursor account shares that computer. Any Bot that can
read `/workspace` can read the token file. Isolation is between Cursor users,
not between your Bots.

## Revoke access

1. Strava → [Settings → My Apps](https://www.strava.com/settings/apps)
2. Revoke the application you created
3. Delete the env file on the computer
4. Remove the custom MCP server from GrokBot if you added one

## Reporting

This is a personal fork. Please do not file Strava activity dumps or live
tokens in GitHub issues.
