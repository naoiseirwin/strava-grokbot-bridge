"""Tests for env-file path selection and permissions."""

from pathlib import Path

from strava_mcp.env import (
    ENV_FILE_VAR,
    get_persistent_env_file,
    restrict_env_file_permissions,
)
from strava_mcp.scopes import DEFAULT_SCOPES, DEFAULT_STRAVA_SCOPES
from strava_mcp.scripts.setup_auth import parse_authorization_code, persist_env_value


def test_persistent_env_file_honors_override(monkeypatch, tmp_path: Path) -> None:
    custom = tmp_path / "custom.env"
    monkeypatch.setenv(ENV_FILE_VAR, str(custom))
    assert get_persistent_env_file() == custom


def test_restrict_env_file_permissions(tmp_path: Path) -> None:
    path = tmp_path / "tokens.env"
    path.write_text("STRAVA_CLIENT_ID=x\n")
    path.chmod(0o644)
    restrict_env_file_permissions(path)
    assert path.stat().st_mode & 0o777 == 0o600


def test_persist_env_value_sets_mode_600(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "tokens.env"
    persist_env_value(path, "STRAVA_CLIENT_ID", "abc")
    assert path.exists()
    assert path.stat().st_mode & 0o777 == 0o600
    assert "STRAVA_CLIENT_ID" in path.read_text()
    assert "abc" in path.read_text()


def test_parse_authorization_code_from_query() -> None:
    url = "http://localhost:18741/callback?state=&code=XYZ123&scope=activity:read"
    assert parse_authorization_code(url) == "XYZ123"


def test_default_scopes_are_read_only() -> None:
    assert "profile:write" not in DEFAULT_SCOPES
    assert "profile:write" not in DEFAULT_STRAVA_SCOPES
    assert "activity:read_all" in DEFAULT_SCOPES
    assert "profile:read_all" in DEFAULT_STRAVA_SCOPES
