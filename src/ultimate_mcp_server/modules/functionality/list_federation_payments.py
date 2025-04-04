from datetime import datetime
from typing import List, Tuple

from ..data_types import ListFederationPaymentsCommand, FederationPayment, Player
from ..utils import get_connection
from ..init_db import init_db


def list_federation_payments(command: ListFederationPaymentsCommand) -> Tuple[Player, List[FederationPayment]]:
    """List all federation payments for a player.
    
    Args:
        command: The command with player name and limit
        
    Returns:
        Tuple containing the player and a list of their federation payments
        
    Raises:
        ValueError: If the player doesn't exist
    """
    init_db(command.db_uri)
    
    conn = get_connection(command.db_uri)
    cursor = conn.cursor()
    
    try:
        # Get player details
        cursor.execute(
            "SELECT name, created, phone, email FROM players WHERE name = ?",
            (command.player_name,)
        )
        player_data = cursor.fetchone()
        if not player_data:
            raise ValueError(f"Player '{command.player_name}' not found")
        
        # Create Player object
        player = Player(
            name=player_data[0],
            created=datetime.fromisoformat(player_data[1]),
            phone=player_data[2],
            email=player_data[3]
        )
        
        # Get federation payments for this player
        cursor.execute(
            """
            SELECT id, player_name, payment_date, amount, notes, created_at
            FROM federation_payments
            WHERE player_name = ?
            ORDER BY payment_date DESC, created_at DESC
            LIMIT ?
            """,
            (command.player_name, command.limit)
        )
        payment_data = cursor.fetchall()
        
        # Create list of FederationPayment objects
        payments = []
        for row in payment_data:
            payments.append(
                FederationPayment(
                    id=row[0],
                    player_name=row[1],
                    payment_date=datetime.fromisoformat(row[2]),
                    amount=row[3],
                    notes=row[4],
                    created_at=datetime.fromisoformat(row[5])
                )
            )
        
        return player, payments
    finally:
        conn.close()