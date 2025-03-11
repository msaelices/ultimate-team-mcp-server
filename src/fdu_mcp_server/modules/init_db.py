import sqlite3
from pathlib import Path

from .constants import DEFAULT_SQLITE_DATABASE_PATH

def init_db(db_path: Path = DEFAULT_SQLITE_DATABASE_PATH) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS players (
        name TEXT PRIMARY KEY,
        created TIMESTAMP,
        phone TEXT,
        email TEXT
    )
    ''')
    
    conn.commit()
    conn.close()