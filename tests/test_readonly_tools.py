"""Read-only tool surface for the GrokBot fork."""

from fastmcp import Client


async def test_star_segment_is_not_registered(mcp) -> None:
    async with Client(mcp) as client:
        tools = await client.list_tools()
        names = [tool.name for tool in tools]

    assert "star_segment" not in names
    assert "query_activities" in names
    assert "get_athlete_profile" in names
    assert "query_segments" in names
    assert "query_routes" in names
