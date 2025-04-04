from datetime import datetime

from ..data_types import ClearPaymentCommand, TournamentPlayer
from ..utils import get_connection
from ..init_db import init_db


def clear_payment(command: ClearPaymentCommand) -> TournamentPlayer:
    """Clear a player's tournament payment status.
    
    Args:
        command: The command with tournament and player details
        
    Returns:
        Updated TournamentPlayer record
        
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
            SELECT tournament_id, player_name, registered_at, has_paid
            FROM tournament_players 
            WHERE tournament_id = ? AND player_name = ?
            """,
            (command.tournament_id, command.player_name)
        )
        registration = cursor.fetchone()
        if not registration:
            raise ValueError(
                f"Player '{command.player_name}' is not registered for tournament {command.tournament_id}"
            )
        
        # If not already paid, nothing to do
        if not registration[3]:
            conn.close()
            return TournamentPlayer(
                tournament_id=command.tournament_id,
                player_name=command.player_name,
                registered_at=datetime.fromisoformat(registration[2]),
                has_paid=False,
                payment_date=None
            )
        
        # Clear payment status
        cursor.execute(
            """
            UPDATE tournament_players
            SET has_paid = 0, payment_date = NULL
            WHERE tournament_id = ? AND player_name = ?
            """,
            (command.tournament_id, command.player_name)
        )
        conn.commit()
        
        # Return updated registration
        return TournamentPlayer(
            tournament_id=command.tournament_id,
            player_name=command.player_name,
            registered_at=datetime.fromisoformat(registration[2]),
            has_paid=False,
            payment_date=None
        )
    except Exception as e:
        conn.rollback()
        raise
    finally:
        conn.close()