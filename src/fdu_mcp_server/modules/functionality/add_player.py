import sqlite3
from datetime import datetime
from pathlib import Path

from ..data_types import AddPlayerCommand, Player
from ..init_db import init_db

def add_player(command: AddPlayerCommand) -> Player:
    init_db(command.db_path)
    
    conn = sqlite3.connect(command.db_path)
    cursor = conn.cursor()
    
    now = datetime.now()
    
    try:
        cursor.execute(
            "INSERT INTO players (name, created, phone, email) VALUES (?, ?, ?, ?)",
            (command.name, now, command.phone, command.email)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise ValueError(f"Player '{command.name}' already exists")
    
    conn.close()
    
    return Player(
        name=command.name,
        created=now,
        phone=command.phone,
        email=command.email
    )