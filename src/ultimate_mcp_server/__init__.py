import asyncio
import logging
import sys
import os
from pathlib import Path

from .server import run_server
from .cli import cli
from .modules.constants import DEFAULT_DB_URI

logger = logging.getLogger(__name__)


def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    # Check if we're running in CLI mode or server mode
    logger.info("Starting Ultimate Team MCP")
    
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
        print("Ultimate Team MCP Server - Ultimate Frisbee Team Management")
        print("Usage: ultimate-team-mcp-server [--db-uri DATABASE_URI]")
        print("")
        print("Options:")
        print("  --db-uri DATABASE_URI  URI to SQLite database")
        print("                        (file:///path/to/db.sqlite or sqlitecloud://host:port/database?apikey=key)")
        print("                        Default is taken from SQLITE_URI environment variable or ~/.ultimate.db")
        print("  --help                Show this help message")
        print("")
        print("Commands:")
        print("  add-player NAME       Add a player to the database")
        print("  list-players          List players in the database")
        print("  remove-player         Remove a player from the database")
        print("  backup PATH           Backup the database to a file")
        print("  import-players CSV    Import players from a CSV file, update existing ones")
        print("")
        print("For more information on a command, run:")
        print("  ultimate-team-mcp-server COMMAND --help")
        return 0

    # Set up environment variables for FastMCP if --db-uri is specified
    for i, arg in enumerate(sys.argv):
        if arg == "--db-uri" and i + 1 < len(sys.argv):
            os.environ["SQLITE_URI"] = sys.argv[i + 1]
            # Remove the args so FastMCP doesn't try to parse them
            sys.argv.pop(i)  # Remove --db-uri
            sys.argv.pop(i)  # Remove the value
            break

    # Run the server
    try:
        # Use FastMCP's run method
        run_server()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
    
    return 0