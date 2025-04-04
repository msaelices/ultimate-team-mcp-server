from ..data_types import UnregisterPlayerCommand
from ..utils import get_connection
from ..init_db import init_db


def unregister_player(command: UnregisterPlayerCommand) -> str:
    """Unregister a player from a tournament.
    
    Args:
        command: The command with player and tournament details
        
    Returns:
        Success message
        
    Raises:
        ValueError: If the player is not registered for the tournament
    """
    init_db(command.db_uri)
    
    conn = get_connection(command.db_uri)
    cursor = conn.cursor()
    
    try:
        # Check if player is registered for this tournament
        cursor.execute(
            """
            SELECT tournament_id, player_name FROM tournament_players 
            WHERE tournament_id = ? AND player_name = ?
            """,
            (command.tournament_id, command.player_name)
        )
        existing = cursor.fetchone()
        if not existing:
            raise ValueError(
                f"Player '{command.player_name}' is not registered for tournament {command.tournament_id}"
            )
        
        # Get tournament name for response message
        cursor.execute("SELECT name FROM tournaments WHERE id = ?", (command.tournament_id,))
        tournament = cursor.fetchone()
        tournament_name = tournament[0] if tournament else f"ID {command.tournament_id}"
        
        # Unregister the player
        cursor.execute(
            """
            DELETE FROM tournament_players 
            WHERE tournament_id = ? AND player_name = ?
            """,
            (command.tournament_id, command.player_name)
        )
        conn.commit()
        
        return f"Player '{command.player_name}' unregistered from tournament '{tournament_name}'"
    except Exception as e:
        conn.rollback()
        raise
    finally:
        conn.close()