from datetime import datetime

from ..data_types import AddFederationPaymentCommand, FederationPayment
from ..utils import get_connection
from ..init_db import init_db


def add_federation_payment(command: AddFederationPaymentCommand) -> FederationPayment:
    """Add a federation payment for a player.
    
    Args:
        command: The command with player and payment details
        
    Returns:
        The created FederationPayment object
        
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
        
        # Current timestamp
        now = datetime.now()
        
        # Add the payment record
        cursor.execute(
            """
            INSERT INTO federation_payments 
            (player_name, payment_date, amount, notes, created_at)
            VALUES (?, ?, ?, ?, ?)
            """, 
            (
                command.player_name, 
                command.payment_date, 
                command.amount, 
                command.notes, 
                now
            )
        )
        conn.commit()
        
        # Get the ID of the newly inserted payment
        payment_id = cursor.lastrowid
        
        return FederationPayment(
            id=payment_id,
            player_name=command.player_name,
            payment_date=command.payment_date,
            amount=command.amount,
            notes=command.notes,
            created_at=now
        )
    except Exception as e:
        conn.rollback()
        raise
    finally:
        conn.close()