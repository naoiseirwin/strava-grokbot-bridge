"""Local configuration wizard for Strava MCP transports."""

from __future__ import annotations

import argparse
import asyncio
import os
import select
import shutil
import sys
import time
import webbrowser
from collections.abc import Iterable
from getpass import getpass
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import httpx
from dotenv import dotenv_values, set_key

from ..env import get_env_file_path, restrict_env_file_permissions
from ..models import TokenResponse
from ..scopes import DEFAULT_SCOPES

STDIO = "stdio"
HTTP = "http"
DEFAULT_CALLBACK_PORT = 18741
CALLBACK_TIMEOUT_SECONDS = 300

_GROKBOT_BANNER = """
GrokBot: this wizard runs on the cloud computer.
Use Take over for Strava login, passkey, or 2FA.
Never paste access tokens, refresh tokens, or client secrets into chat.
""".strip()


def parse_authorization_code(redirect_url: str) -> str:
    """Extract the OAuth code from a Strava redirect URL."""
    parsed = urlparse(redirect_url.strip())
    code = parse_qs(parsed.query).get("code", [""])[0]
    if code:
        return code
    if "code=" in redirect_url:
        return redirect_url.split("code=")[1].split("&")[0]
    raise ValueError("Could not locate authorization code in the redirect URL.")


def persist_env_value(env_path: Path, key: str, value: str) -> None:
    """Write one key and keep the env file owner-only."""
    env_path.parent.mkdir(parents=True, exist_ok=True)
    env_path.touch(exist_ok=True)
    set_key(str(env_path), key, value)
    restrict_env_file_permissions(env_path)


def main(argv: list[str] | None = None) -> None:
    """Run the interactive setup wizard for local Strava MCP configuration."""
    args = _parse_args(argv)

    print("=" * 60)
    print("Strava MCP - Local Setup Wizard")
    print("=" * 60)
    print()
    print(_GROKBOT_BANNER)
    print()
    print("This wizard writes stdio tokens to /workspace/.strava-mcp.env on a")
    print("GrokBot computer (or ~/.strava-mcp.env otherwise). Override with")
    print("STRAVA_MCP_ENV_FILE. HTTP transport is kept for reference only.")
    print()

    modes = _select_modes(args)
    if not modes:
        print("No transport selected. Exiting.")
        return

    env_path = _ensure_env_file()
    existing = dotenv_values(str(env_path)) if env_path.exists() else {}

    print()
    print("Step 1: Strava API credentials")
    print("-" * 60)
    print("Create your own app at https://www.strava.com/settings/api")
    print("Authorization Callback Domain must be: localhost")
    print("App display name must not imply an official Strava product")
    print("(for example: 'GrokBot Activity Bridge'). Compatible with Strava.")
    print()

    client_id = _resolve_client_id(existing)
    client_secret = _resolve_client_secret(existing)
    if not client_id or not client_secret:
        _print_missing_credentials_help()
        sys.exit(1)

    persist_env_value(env_path, "STRAVA_CLIENT_ID", client_id)
    persist_env_value(env_path, "STRAVA_CLIENT_SECRET", client_secret)

    if STDIO in modes:
        _configure_stdio(
            env_path,
            client_id,
            client_secret,
            open_browser=not args.no_browser,
            callback_port=args.callback_port,
        )

    if HTTP in modes:
        _configure_http(env_path, existing)

    print("=" * 60)
    print("Configuration complete!")
    selected = " & ".join(sorted(modes))
    print(f"Updated {env_path} for transport mode(s): {selected}")
    print("Next: add a custom stdio MCP command in GrokBot chat. See README.")
    print("=" * 60)


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Configure Strava MCP authentication")
    parser.add_argument(
        "--stdio",
        action="store_true",
        help="Configure stdio tokens only (GrokBot default)",
    )
    parser.add_argument(
        "--http",
        action="store_true",
        help="Configure HTTP transport (not the GrokBot product)",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not open a browser; still listen for the localhost callback",
    )
    parser.add_argument(
        "--callback-port",
        type=int,
        default=DEFAULT_CALLBACK_PORT,
        help=f"localhost port for the OAuth redirect (default {DEFAULT_CALLBACK_PORT})",
    )
    return parser.parse_args(argv)


def _select_modes(args: argparse.Namespace) -> set[str]:
    if args.stdio and args.http:
        return {STDIO, HTTP}
    if args.stdio:
        return {STDIO}
    if args.http:
        return {HTTP}
    if not sys.stdin.isatty():
        return {STDIO}
    return _prompt_modes()


def _prompt_modes() -> set[str]:
    """Prompt the user to choose which transport(s) to configure."""
    choices = {
        "1": {STDIO},
        "2": {HTTP},
        "3": {STDIO, HTTP},
        "": {STDIO},
    }
    print("Select transport mode to configure:")
    print("  1) stdio  (GrokBot cloud computer / single-user) [default]")
    print("  2) http   (not used for GrokBot)")
    print("  3) both")
    print()

    while True:
        choice = input("Enter choice [1-3]: ").strip()
        if choice in choices:
            return choices[choice]
        print("Invalid selection. Please enter 1, 2, or 3.")


def _existing_or_env(existing: dict[str, str | None], key: str) -> str:
    value = os_env(key) or (existing.get(key) or "")
    if value in {"", "your_client_id_here", "your_client_secret_here"}:
        return ""
    return value


def os_env(key: str) -> str:
    return os.environ.get(key, "").strip()


def _resolve_client_id(existing: dict[str, str | None]) -> str:
    current = _existing_or_env(existing, "STRAVA_CLIENT_ID")
    if current:
        print("Using STRAVA_CLIENT_ID already present on this computer.")
        return current
    if not sys.stdin.isatty():
        return ""
    return _prompt_required("Strava Client ID", None)


def _resolve_client_secret(existing: dict[str, str | None]) -> str:
    current = _existing_or_env(existing, "STRAVA_CLIENT_SECRET")
    if current:
        print("Using STRAVA_CLIENT_SECRET already present on this computer.")
        return current
    if not sys.stdin.isatty():
        return ""
    return _prompt_secret("Strava Client Secret", None)


def _print_missing_credentials_help() -> None:
    print()
    print("Missing STRAVA_CLIENT_ID and/or STRAVA_CLIENT_SECRET on this computer.")
    print("Do not paste them into chat.")
    print("Put them on the computer, then re-run: strava-mcp auth --stdio")
    print("  - GrokBot secret-request, written into /workspace/.strava-mcp.env, or")
    print("  - environment variables on the stdio MCP server entry")


def _prompt_required(prompt_text: str, default: str | None = None) -> str:
    """Prompt for a required value, offering a default if provided."""
    while True:
        prompt = f"{prompt_text}"
        if default:
            prompt += f" [{default}]"
        prompt += ": "
        value = input(prompt).strip()
        if value:
            return value
        if default:
            return default
        print("This value is required.")


def _prompt_secret(prompt_text: str, default: str | None = None) -> str:
    """Prompt for sensitive input (client secret)."""
    masked = "****" if default else None
    while True:
        prompt = f"{prompt_text}"
        if masked:
            prompt += " [press Enter to keep existing]"
        prompt += ": "
        value = getpass(prompt).strip()
        if value:
            return value
        if default:
            return default
        print("This value is required.")


def _prompt_optional(prompt_text: str, default: str | None = None) -> str | None:
    """Prompt for an optional value, returning None if left blank with no default."""
    prompt = f"{prompt_text}"
    if default:
        prompt += f" [{default}]"
    prompt += ": "
    value = input(prompt).strip()
    if value:
        return value
    return default


def _ensure_env_file() -> Path:
    """Ensure the selected env file exists, copying from .env.example if available."""
    env_path = get_env_file_path()
    example_path = Path.cwd() / ".env.example"
    if env_path.exists():
        restrict_env_file_permissions(env_path)
        return env_path

    env_path.parent.mkdir(parents=True, exist_ok=True)
    if example_path.exists():
        shutil.copy(example_path, env_path)
        print(f"Created {env_path} from {example_path.name}")
    else:
        env_path.touch()
        print(f"Created empty {env_path} (no .env.example found)")
    restrict_env_file_permissions(env_path)
    return env_path


def build_authorize_url(client_id: str, redirect_uri: str, scopes: str = DEFAULT_SCOPES) -> str:
    """Build the Strava OAuth authorize URL for stdio setup."""
    return (
        "https://www.strava.com/oauth/authorize"
        f"?client_id={client_id}"
        "&response_type=code"
        f"&redirect_uri={redirect_uri}"
        "&approval_prompt=force"
        f"&scope={scopes}"
    )


def _configure_stdio(
    env_path: Path,
    client_id: str,
    client_secret: str,
    *,
    open_browser: bool,
    callback_port: int,
) -> None:
    """Run stdio setup, exchanging OAuth tokens and persisting them."""
    print()
    print("Step 2 (stdio): Authorize the application")
    print("-" * 60)

    print("Scopes requested (read-only):")
    print(f"  {DEFAULT_SCOPES}")
    print()
    print("A browser on THIS computer should open Strava's consent screen.")
    print("If you need a password, passkey, or 2FA, use Take over.")
    print("Do not paste the redirect URL or tokens into GrokBot chat.")
    print()

    redirect_uri = f"http://localhost:{callback_port}/callback"
    auth_url = build_authorize_url(client_id, redirect_uri)

    print("Authorization URL:")
    print(auth_url)
    print()

    if open_browser:
        opened = webbrowser.open(auth_url)
        if opened:
            print("Opened the computer browser. Waiting for the localhost redirect.")
        else:
            print("Could not open a browser automatically. Open the URL above on this computer.")

    code = _wait_for_callback_code(callback_port, CALLBACK_TIMEOUT_SECONDS)
    if not code:
        print()
        print("No callback received on this computer.")
        if sys.stdin.isatty():
            print("Paste the full redirect URL here in this terminal (not in chat).")
            redirect_url = input("Redirect URL: ").strip()
            try:
                code = parse_authorization_code(redirect_url)
            except ValueError as exc:
                print(f"Error: {exc}")
                return
        else:
            print("Re-run `strava-mcp auth --stdio` with Take over on the computer.")
            return

    print()
    print("Exchanging authorization code for tokens...")
    print("-" * 60)

    try:
        token_data = asyncio.run(_exchange_token(client_id, client_secret, code))
    except Exception as exc:  # noqa: BLE001 - surface any unexpected error
        print(f"Error: Failed to exchange code for tokens: {exc}")
        return

    if token_data is None:
        return

    persist_env_value(env_path, "STRAVA_ACCESS_TOKEN", token_data.access_token)
    persist_env_value(env_path, "STRAVA_REFRESH_TOKEN", token_data.refresh_token)

    print()
    print(f"stdio tokens saved to {env_path} (mode 600)")
    if token_data.athlete:
        athlete = token_data.athlete
        name = f"{athlete.firstname} {athlete.lastname}".strip()
        if name:
            print(f"Authenticated as: {name}")
    print()


class _CallbackServer(HTTPServer):
    auth_code: str | None = None
    auth_error: str | None = None


class _CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)
        code = qs.get("code", [None])[0]
        error = qs.get("error", [None])[0]
        server = self.server
        assert isinstance(server, _CallbackServer)
        server.auth_code = code
        server.auth_error = error

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        if code:
            body = (
                "<html><body><h1>Strava authorization complete</h1>"
                "<p>You can close this tab. If this is the GrokBot computer, "
                "return to chat.</p></body></html>"
            )
        else:
            body = (
                "<html><body><h1>Authorization did not complete</h1>"
                f"<p>{error or 'missing code'}</p></body></html>"
            )
        self.wfile.write(body.encode())

    def log_message(self, format: str, *args: object) -> None:  # noqa: A003
        return


def _wait_for_callback_code(port: int, timeout: float) -> str | None:
    """Serve a localhost callback until Strava redirects with a code."""
    try:
        server = _CallbackServer(("127.0.0.1", port), _CallbackHandler)
    except OSError as exc:
        print(f"Could not bind localhost:{port}: {exc}")
        return None

    print(f"Listening on http://127.0.0.1:{port}/callback for {int(timeout)}s...")
    deadline = time.monotonic() + timeout
    try:
        while time.monotonic() < deadline:
            ready, _, _ = select.select([server.socket], [], [], 1.0)
            if not ready:
                continue
            server.handle_request()
            if server.auth_error:
                print(f"Strava returned error: {server.auth_error}")
                return None
            if server.auth_code:
                return server.auth_code
    finally:
        server.server_close()
    return None


def _configure_http(env_path: Path, existing: dict[str, str | None]) -> None:
    """Prompt for HTTP transport environment settings."""
    print()
    print("Step 2 (http): Configure HTTP transport settings")
    print("-" * 60)
    print("HTTP / Lambda / ngrok is not how GrokBot users run this fork.")
    print()

    host = _prompt_optional(
        "Server host (STRAVA_MCP_HOST)",
        existing.get("STRAVA_MCP_HOST") or "127.0.0.1",
    )
    port = _prompt_optional(
        "Server port (STRAVA_MCP_PORT)",
        existing.get("STRAVA_MCP_PORT") or "8000",
    )
    base_url = _prompt_optional(
        "Public base URL (STRAVA_MCP_BASE_URL) [leave blank for auto]",
        existing.get("STRAVA_MCP_BASE_URL") or "",
    )
    http_path = _prompt_optional(
        "Path prefix (STRAVA_MCP_PATH)",
        existing.get("STRAVA_MCP_PATH") or "/mcp",
    )

    measurement = _prompt_optional(
        "Measurement preference (meters|feet)",
        existing.get("STRAVA_MEASUREMENT_PREFERENCE") or "meters",
    )
    export_path = _prompt_optional(
        "Route export path (ROUTE_EXPORT_PATH)",
        existing.get("ROUTE_EXPORT_PATH") or "./exports",
    )

    scopes = _prompt_optional(
        "OAuth scopes (STRAVA_OAUTH_SCOPES)",
        existing.get("STRAVA_OAUTH_SCOPES") or DEFAULT_SCOPES,
    )
    clients = _prompt_optional(
        "Registered MCP clients (STRAVA_MCP_OAUTH_CLIENTS)",
        existing.get("STRAVA_MCP_OAUTH_CLIENTS"),
    )

    backend = _prompt_optional(
        "Session backend (memory|dynamodb)",
        existing.get("STRAVA_SESSION_BACKEND") or "memory",
    )

    dynamo_table = dynamo_region = ttl_seconds = None
    if backend and backend.lower() == "dynamodb":
        print()
        print("DynamoDB configuration:")
        dynamo_table = _prompt_optional(
            "Table name (STRAVA_SESSION_TABLE)",
            existing.get("STRAVA_SESSION_TABLE"),
        )
        dynamo_region = _prompt_optional(
            "AWS region (AWS_REGION/AWS_DEFAULT_REGION)",
            existing.get("AWS_REGION") or existing.get("AWS_DEFAULT_REGION"),
        )
        ttl_seconds = _prompt_optional(
            "Session TTL seconds (STRAVA_SESSION_TTL_SECONDS)",
            existing.get("STRAVA_SESSION_TTL_SECONDS"),
        )

    _set_keys(
        env_path,
        (
            ("STRAVA_MCP_HOST", host),
            ("STRAVA_MCP_PORT", port),
            ("STRAVA_MCP_BASE_URL", base_url or None),
            ("STRAVA_MCP_PATH", http_path),
            ("STRAVA_MEASUREMENT_PREFERENCE", measurement),
            ("ROUTE_EXPORT_PATH", export_path),
            ("STRAVA_OAUTH_SCOPES", scopes),
            ("STRAVA_MCP_OAUTH_CLIENTS", clients),
            ("STRAVA_SESSION_BACKEND", backend),
            ("STRAVA_SESSION_TABLE", dynamo_table),
            ("AWS_REGION", dynamo_region),
            ("STRAVA_SESSION_TTL_SECONDS", ttl_seconds),
        ),
    )
    restrict_env_file_permissions(env_path)

    print()
    print(f"HTTP environment values updated in {env_path}.")
    print("When running from source, install HTTP dependencies with: uv sync --extra http")
    print()


def _set_keys(env_path: Path, pairs: Iterable[tuple[str, str | None]]) -> None:
    """Persist non-empty key/value pairs to the selected env file."""
    for key, value in pairs:
        if value is None:
            continue
        persist_env_value(env_path, key, value)


async def _exchange_token(
    client_id: str,
    client_secret: str,
    code: str,
) -> TokenResponse | None:
    """Exchange authorization code for tokens using Strava's OAuth endpoint."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://www.strava.com/oauth/token",
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "code": code,
                "grant_type": "authorization_code",
            },
        )

        if response.status_code != 200:
            print(
                f"Error: Token exchange failed with status {response.status_code}",
            )
            print(response.text)
            return None

        return TokenResponse(**response.json())


if __name__ == "__main__":
    main()
