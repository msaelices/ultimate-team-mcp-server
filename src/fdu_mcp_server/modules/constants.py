import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection URI
# Can be either:
# - sqlitecloud://hostname:port/database?apikey=apikey
# - file:///path/to/local/database.db
DEFAULT_DB_URI = os.getenv("SQLITE_URI", f"file://{Path.cwd() / 'db' / 'fdu.db'}")

# Keep legacy path for backward compatibility
DEFAULT_SQLITE_DATABASE_PATH = Path.cwd() / "db" / "fdu.db"