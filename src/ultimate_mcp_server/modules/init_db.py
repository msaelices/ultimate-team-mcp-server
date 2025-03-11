from pathlib import Path

from .constants import DEFAULT_SQLITE_DATABASE_PATH, SQLITECLOUD_CONNECTION_STRING
from .utils import get_connection


def init_db(db_path: Path = DEFAULT_SQLITE_DATABASE_PATH) -> None:
    """Initialize database with required tables.

    For SQLite local database, creates directory if needed.
    For SQLiteCloud, connects and creates tables if needed.
    """
    # For local SQLite, ensure directory exists
    if (
        not SQLITECLOUD_CONNECTION_STRING.startswith("sqlitecloud://")
        or "localhost" in SQLITECLOUD_CONNECTION_STRING
    ):
        db_path.parent.mkdir(parents=True, exist_ok=True)

    # Get connection using utility function
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS players (
        name TEXT PRIMARY KEY,
        created TIMESTAMP,
        phone TEXT,
        email TEXT
    )
    """)

    conn.commit()
    conn.close()

