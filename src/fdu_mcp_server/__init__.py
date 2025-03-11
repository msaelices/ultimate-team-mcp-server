import sys
from pathlib import Path

from .server import serve
from .cli import cli
from .import_csv import import_csv

def main():
    # Check if we're running in CLI mode or server mode
    if len(sys.argv) > 1:
        if sys.argv[1] in ["add-player", "list-players", "remove-player", "backup"]:
            return cli()
        elif sys.argv[1] == "import-csv":
            # Remove the first argument and pass the rest to import_csv
            sys.argv = [sys.argv[0]] + sys.argv[2:]
            return import_csv()
    
    # Default to server mode
    if "--help" in sys.argv or len(sys.argv) <= 1:
        print("FDU MCP Server - Ultimate Frisbee Team Management")
        print("Usage: fdu-mcp-server [--db DATABASE_PATH]")
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
        print("  import-csv CSV_FILE Import players from a CSV file")
        print("")
        print("For more information on a command, run:")
        print("  fdu-mcp-server COMMAND --help")
        return 0
    
    db_path = None
    if "--db" in sys.argv:
        idx = sys.argv.index("--db")
        if idx + 1 < len(sys.argv):
            db_path = Path(sys.argv[idx + 1])
    
    serve(db_path)
    return 0

if __name__ == "__main__":
    sys.exit(main())