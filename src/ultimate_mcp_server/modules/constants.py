import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection URI
# Can be either:
# - sqlitecloud://hostname:port/database?apikey=apikey
# - file:///path/to/local/database.db
DEFAULT_DB_URI = f"file://{Path.cwd() / 'ultimate.db'}"
DB_URI = os.getenv("DB_URI", DEFAULT_DB_URI)

