import sqlite3

from ..data_types import RemovePlayerCommand
from ..init_db import init_db

def remove_player(command: RemovePlayerCommand) -> bool:
    init_db(command.db_path)
    
    conn = sqlite3.connect(command.db_path)
    cursor = conn.cursor()
    
    cursor.execute(
        "DELETE FROM players WHERE name = ?",
        (command.name,)
    )
    
    found = cursor.rowcount > 0
    conn.commit()
    conn.close()
    
    if not found:
        raise ValueError(f"Player '{command.name}' not found")
    
    return True