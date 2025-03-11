from datetime import datetime

from ..data_types import AddPlayerCommand, Player
from ..init_db import init_db
from ..utils import get_connection

def add_player(command: AddPlayerCommand) -> Player:
    init_db(command.db_uri)
    
    conn = get_connection(command.db_uri)
    cursor = conn.cursor()
    
    now = datetime.now()
    
    try:
        cursor.execute(
            "INSERT INTO players (name, created, phone, email) VALUES (?, ?, ?, ?)",
            (command.name, now, command.phone, command.email)
        )
        conn.commit()
    except Exception as e:
        conn.close()
        # Handle both sqlite3.IntegrityError and sqlitecloud equivalent
        if "UNIQUE constraint failed" in str(e) or "already exists" in str(e):
            raise ValueError(f"Player '{command.name}' already exists")
        raise
    
    conn.close()
    
    return Player(
        name=command.name,
        created=now,
        phone=command.phone,
        email=command.email
    )