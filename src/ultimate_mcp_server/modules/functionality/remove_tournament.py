from ..data_types import RemoveTournamentCommand
from ..init_db import init_db
from ..utils import get_connection


def remove_tournament(command: RemoveTournamentCommand) -> str:
    """Remove a tournament from the database.

    Args:
        command: The command containing the tournament ID to remove

    Returns:
        Success message

    Raises:
        ValueError: If tournament with the given ID doesn't exist
    """
    init_db(command.db_uri)
    
    conn = get_connection(command.db_uri)
    cursor = conn.cursor()
    
    # First check if the tournament exists
    cursor.execute("SELECT name FROM tournaments WHERE id = ?", (command.id,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        raise ValueError(f"Tournament with ID {command.id} not found")
        
    tournament_name = result[0]
    
    try:
        cursor.execute("DELETE FROM tournaments WHERE id = ?", (command.id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        conn.close()
    
    return f"Tournament '{tournament_name}' removed successfully"