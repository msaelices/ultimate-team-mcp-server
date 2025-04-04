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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tournaments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        location TEXT NOT NULL,
        date TEXT NOT NULL,
        surface TEXT NOT NULL CHECK(surface IN ('grass', 'beach')),
        registration_deadline TEXT NOT NULL,
        created TIMESTAMP NOT NULL
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tournament_players (
        tournament_id INTEGER,
        player_name TEXT,
        registered_at TIMESTAMP NOT NULL,
        has_paid BOOLEAN NOT NULL DEFAULT 0,
        payment_date TIMESTAMP NULL,
        PRIMARY KEY (tournament_id, player_name),
        FOREIGN KEY (tournament_id) REFERENCES tournaments(id) ON DELETE CASCADE,
        FOREIGN KEY (player_name) REFERENCES players(name) ON DELETE CASCADE
    )
    """)

    conn.commit()
    conn.close()
