import asyncio
import logging
import sys
from pathlib import Path

from .server import serve
from .cli import cli


logger = logging.getLogger(__name__)


def main():
    # Check if we're running in CLI mode or server mode
    logger.info("Starting FDU MCP")
    if len(sys.argv) > 1:
        if sys.argv[1] in [
            "add-player",
            "list-players",
            "remove-player",
            "backup",
            "import-players",
        ]:
            return cli()

    # Default to server mode
    if "--help" in sys.argv:
        print("FDU MCP Server - Ultimate Frisbee Team Management")
        print("Usage: ultimate-team-mcp-server [--db DATABASE_PATH]")
        print("")
        print("Options:")
        print("  --db DATABASE_PATH  Path to the SQLite database (default: ~/.fdu.db)")
        print("  --help              Show this help message")
        print("")
        print("Commands:")
        print("  add-player NAME     Add a player to the database")
        print("  list-players        List players in the database")
        print("  remove-player       Remove a player from the database")
        print("  backup PATH         Backup the database to a file")
        print("  import-csv CSV_FILE Import players from a CSV file (deprecated)")
        print(
            "  import-players CSV  Import players from a CSV file, update existing ones"
        )
        print("")
        print("For more information on a command, run:")
        print("  ultimate-team-mcp-server COMMAND --help")
        return 0

    # Run the server
    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
    return 0
