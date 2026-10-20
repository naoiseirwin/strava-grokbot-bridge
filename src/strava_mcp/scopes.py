"""OAuth scopes for this GrokBot fork.

v1 is read-only. Upstream eddmann/strava-mcp also requested ``profile:write``
for ``star_segment``; that tool is not registered here.
"""

READ_SCOPES: tuple[str, ...] = (
    "profile:read_all",
    "activity:read_all",
    "activity:read",
)

DEFAULT_SCOPES = ",".join(READ_SCOPES)
DEFAULT_STRAVA_SCOPES: list[str] = list(READ_SCOPES)
