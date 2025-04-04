from datetime import datetime
from typing import Optional

from ..data_types import RemoveLastFederationPaymentCommand, FederationPayment
from ..utils import get_connection
from ..init_db import init_db


def remove_last_federation_payment(command: RemoveLastFederationPaymentCommand) -> Optional[FederationPayment]:
    """Remove the most recent federation payment for a player.
    
    Args:
        command: The command with player name
        
    Returns:
        The removed federation payment or None if no payments exist
        
    Raises:
        ValueError: If the player doesn't exist
    """
    init_db(command.db_uri)
    
    conn = get_connection(command.db_uri)
    cursor = conn.cursor()
    
    try:
        # Check if player exists
        cursor.execute(
            "SELECT name FROM players WHERE name = ?", 
            (command.player_name,)
        )
        player = cursor.fetchone()
        if not player:
            raise ValueError(f"Player '{command.player_name}' not found")
        
        # Find the latest payment for this player
        cursor.execute(
            """
            SELECT id, player_name, payment_date, amount, notes, created_at 
            FROM federation_payments 
            WHERE player_name = ?
            ORDER BY payment_date DESC, created_at DESC
            LIMIT 1
            """, 
            (command.player_name,)
        )
        payment = cursor.fetchone()
        
        # If no payments found, return None
        if not payment:
            return None
        
        # Save payment details for return
        removed_payment = FederationPayment(
            id=payment[0],
            player_name=payment[1],
            payment_date=datetime.fromisoformat(payment[2]),
            amount=payment[3],
            notes=payment[4],
            created_at=datetime.fromisoformat(payment[5])
        )
        
        # Delete the payment
        cursor.execute(
            "DELETE FROM federation_payments WHERE id = ?", 
            (payment[0],)
        )
        conn.commit()
        
        return removed_payment
    except Exception as e:
        conn.rollback()
        raise
    finally:
        conn.close()