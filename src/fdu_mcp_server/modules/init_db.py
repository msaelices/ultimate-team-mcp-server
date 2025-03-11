import os
from pathlib import Path
from urllib.parse import urlparse

from .constants import DEFAULT_DB_URI, DEFAULT_SQLITE_DATABASE_PATH
from .utils import get_connection

def init_db(db_uri: str = DEFAULT_DB_URI) -> None:
    """Initialize database with required tables.
    
    For SQLite local database, creates directory if needed.
    For SQLiteCloud, connects and creates tables if needed.
    
    Args:
        db_uri: Database URI (sqlitecloud:// or file://)
    """
    # For local SQLite, ensure directory exists
    parsed_uri = urlparse(db_uri)
    if parsed_uri.scheme == 'file':
        # Extract the path from the URI
        db_path = parsed_uri.path
        if os.name == 'nt' and db_path.startswith('/'):
            db_path = db_path[1:]
        
        # Create directory if it doesn't exist
        path_obj = Path(db_path)
        path_obj.parent.mkdir(parents=True, exist_ok=True)
    
    # Get connection using utility function
    conn = get_connection(db_uri)
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