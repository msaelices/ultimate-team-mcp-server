from pathlib import Path

from .constants import DEFAULT_DB_URI
from .utils import get_connection


def init_db(db_uri: str = DEFAULT_DB_URI) -> None:
    """Initialize database with required tables.

    For SQLite local database, creates directory if needed.
    For SQLiteCloud, connects and creates tables if needed.
    """
    # For local SQLite, ensure directory exists
    if db_uri.startswith("file://"):
        db_path = Path(db_uri.replace("file://", ""))
        db_path.parent.mkdir(parents=True, exist_ok=True)

    # Get connection using utility function
    conn = get_connection(db_uri)
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
