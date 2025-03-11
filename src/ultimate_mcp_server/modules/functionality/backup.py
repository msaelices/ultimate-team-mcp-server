import os
import sqlite3
import sqlitecloud
from pathlib import Path
from urllib.parse import urlparse

from ..data_types import BackupCommand
from ..init_db import init_db
from ..utils import get_connection

def backup(command: BackupCommand) -> str:
    init_db(command.db_uri)
    
    # Ensure backup path parent directory exists
    command.backup_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Check database URI type
    parsed_uri = urlparse(command.db_uri)
    
    if parsed_uri.scheme == 'sqlitecloud':
        # SQLiteCloud connection - need to export data through queries
        conn = get_connection(command.db_uri)
        
        # Create a local SQLite backup file
        backup_conn = sqlite3.connect(command.backup_path)
        backup_cursor = backup_conn.cursor()
        
        # Create the schema
        backup_cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            name TEXT PRIMARY KEY,
            created TIMESTAMP,
            phone TEXT,
            email TEXT
        )
        ''')
        
        # Export data
        cursor = conn.cursor()
        cursor.execute("SELECT name, created, phone, email FROM players")
        rows = cursor.fetchall()
        
        for row in rows:
            backup_cursor.execute(
                "INSERT INTO players (name, created, phone, email) VALUES (?, ?, ?, ?)",
                row
            )
        
        backup_conn.commit()
        backup_conn.close()
        conn.close()
    else:
        # Local SQLite connection - we can use the native backup function
        if parsed_uri.scheme == 'file':
            # Extract the path from the URI
            db_path = parsed_uri.path
            if os.name == 'nt' and db_path.startswith('/'):
                db_path = db_path[1:]
        else:
            # Assume it's a direct path (for backward compatibility)
            db_path = command.db_uri
        
        # Connect to the database
        conn = sqlite3.connect(db_path)
        
        # Create a new connection for the backup
        backup_conn = sqlite3.connect(command.backup_path)
        
        # Copy the database
        conn.backup(backup_conn)
        
        # Close connections
        backup_conn.close()
        conn.close()
    
    return f"Successfully backed up database to {command.backup_path}"