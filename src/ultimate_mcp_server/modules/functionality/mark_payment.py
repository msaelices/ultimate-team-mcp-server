from datetime import datetime

from ..data_types import MarkPaymentCommand, TournamentPlayer
from ..utils import get_connection
from ..init_db import init_db


def mark_payment(command: MarkPaymentCommand) -> TournamentPlayer:
    """Mark a player's tournament registration as paid.
    
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
            SELECT tournament_id, player_name, registered_at, has_paid, payment_date
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
        
        # Set payment date to now if not specified
        payment_date = command.payment_date if command.payment_date else datetime.now()
        
        # Update payment status
        cursor.execute(
            """
            UPDATE tournament_players
            SET has_paid = 1, payment_date = ?
            WHERE tournament_id = ? AND player_name = ?
            """,
            (payment_date, command.tournament_id, command.player_name)
        )
        conn.commit()
        
        # Get tournament and player details for response
        cursor.execute(
            """
            SELECT t.name, p.name, p.phone, p.email
            FROM tournaments t, players p
            WHERE t.id = ? AND p.name = ?
            """,
            (command.tournament_id, command.player_name)
        )
        details = cursor.fetchone()
        
        # Return updated registration
        return TournamentPlayer(
            tournament_id=command.tournament_id,
            player_name=command.player_name,
            registered_at=datetime.fromisoformat(registration[2]),
            has_paid=True,
            payment_date=payment_date
        )
    except Exception as e:
        conn.rollback()
        raise
    finally:
        conn.close()