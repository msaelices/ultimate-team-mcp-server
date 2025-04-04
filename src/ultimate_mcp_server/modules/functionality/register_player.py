from datetime import datetime

from ..data_types import RegisterPlayerCommand, TournamentPlayer
from ..utils import get_connection
from ..init_db import init_db


def register_player(command: RegisterPlayerCommand) -> TournamentPlayer:
    """Register a player for a tournament.
    
    Args:
        command: The command with player and tournament details
        
    Returns:
        A TournamentPlayer object representing the registration
        
    Raises:
        ValueError: If the tournament or player doesn't exist, 
                    or if registration deadline has passed,
                    or if the player is already registered
    """
    init_db(command.db_uri)
    
    conn = get_connection(command.db_uri)
    cursor = conn.cursor()
    
    try:
        # Check if tournament exists
        cursor.execute(
            "SELECT id, registration_deadline FROM tournaments WHERE id = ?", 
            (command.tournament_id,)
        )
        tournament = cursor.fetchone()
        if not tournament:
            raise ValueError(f"Tournament with ID {command.tournament_id} not found")
        
        # Check if registration deadline has passed
        deadline = datetime.fromisoformat(tournament[1]).date()
        if deadline < datetime.now().date():
            raise ValueError(f"Registration deadline ({deadline}) has passed")
        
        # Check if player exists
        cursor.execute(
            "SELECT name FROM players WHERE name = ?", 
            (command.player_name,)
        )
        player = cursor.fetchone()
        if not player:
            raise ValueError(f"Player '{command.player_name}' not found")
        
        # Check if player is already registered
        cursor.execute(
            """
            SELECT tournament_id, player_name FROM tournament_players 
            WHERE tournament_id = ? AND player_name = ?
            """, 
            (command.tournament_id, command.player_name)
        )
        existing = cursor.fetchone()
        if existing:
            raise ValueError(
                f"Player '{command.player_name}' is already registered for this tournament"
            )
        
        # Register the player
        now = datetime.now()
        cursor.execute(
            """
            INSERT INTO tournament_players 
            (tournament_id, player_name, registered_at, has_paid, payment_date)
            VALUES (?, ?, ?, 0, NULL)
            """, 
            (command.tournament_id, command.player_name, now)
        )
        conn.commit()
        
        return TournamentPlayer(
            tournament_id=command.tournament_id,
            player_name=command.player_name,
            registered_at=now,
            has_paid=False,
            payment_date=None
        )
    except Exception as e:
        conn.rollback()
        raise
    finally:
        conn.close()