"""Command-line entry point for Strava MCP."""

import sys


def main() -> None:
    """Run the MCP server or a supported subcommand."""
    args = sys.argv[1:]

    if args and args[0] == "auth":
        from .scripts.setup_auth import main as auth_main

        auth_main(args[1:])
        return

    from .server import main as server_main

    server_main()


if __name__ == "__main__":
    main()
