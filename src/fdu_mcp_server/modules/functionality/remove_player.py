from ..data_types import RemovePlayerCommand
from ..init_db import init_db
from ..utils import get_connection

def remove_player(command: RemovePlayerCommand) -> bool:
    init_db(command.db_uri)
    
    conn = get_connection(command.db_uri)
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