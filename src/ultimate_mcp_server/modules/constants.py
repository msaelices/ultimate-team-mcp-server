import os
from pathlib import Path

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # dotenv is optional
    pass

# Get user's home directory for default database path
HOME_DIR = Path.home()
DEFAULT_LOCAL_DB_PATH = HOME_DIR / ".ultimate.db"

# Database connection URI
# Can be either:
# - sqlitecloud://hostname:port/database?apikey=apikey
# - file:///path/to/local/database.db
# Priority:
# 1. SQLITE_URI environment variable (FastMCP default)
# 3. Default local file path
DEFAULT_DB_URI = os.getenv("SQLITE_URI", f"file://{DEFAULT_LOCAL_DB_PATH}")

