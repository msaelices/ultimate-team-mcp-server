import sqlite3
import shutil
from pathlib import Path

from ..data_types import BackupCommand
from ..init_db import init_db

def backup(command: BackupCommand) -> str:
    init_db(command.db_path)
    
    # Ensure backup path parent directory exists
    command.backup_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Connect to the database and backup
    conn = sqlite3.connect(command.db_path)
    
    # Create a new connection for the backup
    backup_conn = sqlite3.connect(command.backup_path)
    
    # Copy the database
    conn.backup(backup_conn)
    
    # Close connections
    backup_conn.close()
    conn.close()
    
    return f"Successfully backed up database to {command.backup_path}"