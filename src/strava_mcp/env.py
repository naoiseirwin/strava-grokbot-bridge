"""Environment file locations for Strava MCP configuration."""

from __future__ import annotations

import os
from pathlib import Path

ENV_FILE_VAR = "STRAVA_MCP_ENV_FILE"
LOCAL_ENV_FILE = Path(".env")
HOME_ENV_FILE = Path.home() / ".strava-mcp.env"
WORKSPACE_DIR = Path("/workspace")
WORKSPACE_ENV_FILE = WORKSPACE_DIR / ".strava-mcp.env"

# Back-compat name: persistent file used when no override and no local .env.
DEFAULT_ENV_FILE = WORKSPACE_ENV_FILE if WORKSPACE_DIR.is_dir() else HOME_ENV_FILE


def get_persistent_env_file() -> Path:
    """Return the persistent env file (GrokBot: /workspace, else home)."""
    override = os.environ.get(ENV_FILE_VAR)
    if override:
        return Path(override).expanduser()
    if WORKSPACE_DIR.is_dir():
        return WORKSPACE_ENV_FILE
    return HOME_ENV_FILE


def get_env_file_path() -> Path:
    """Get the env file path interactive setup should write to."""
    local_env = Path.cwd() / LOCAL_ENV_FILE
    if local_env.exists():
        return local_env
    return get_persistent_env_file()


def get_env_files() -> tuple[str, str]:
    """Return env files in precedence order for settings loaders."""
    return (str(get_persistent_env_file()), str(LOCAL_ENV_FILE))


def restrict_env_file_permissions(path: Path) -> None:
    """Restrict an env file to owner read/write (mode 600)."""
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass
