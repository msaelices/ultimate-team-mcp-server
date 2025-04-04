from datetime import datetime
from typing import List, Tuple, Dict
from dataclasses import dataclass

from ..data_types import ListTournamentPlayersCommand, Player, Tournament
from ..utils import get_connection
from ..init_db import init_db


@dataclass
class PlayerWithPayment:
    player: Player
    has_paid: bool
    payment_date: datetime = None


def list_tournament_players(command: ListTournamentPlayersCommand) -> Tuple[Tournament, List[PlayerWithPayment]]:
    """List all players registered for a tournament with payment status.
    
    Args:
        command: The command with tournament ID and limit
        
    Returns:
        Tuple containing the tournament and a list of registered players with payment info
        
    Raises:
        ValueError: If the tournament doesn't exist
    """
    init_db(command.db_uri)
    
    conn = get_connection(command.db_uri)
    cursor = conn.cursor()
    
    try:
        # Get tournament details
        cursor.execute(
            """
            SELECT id, name, location, date, surface, registration_deadline, created 
            FROM tournaments WHERE id = ?
            """,
            (command.tournament_id,)
        )
        tournament_data = cursor.fetchone()
        if not tournament_data:
            raise ValueError(f"Tournament with ID {command.tournament_id} not found")
        
        from ..data_types import SurfaceType, Tournament
        tournament = Tournament(
            id=tournament_data[0],
            name=tournament_data[1],
            location=tournament_data[2],
            date=datetime.fromisoformat(tournament_data[3]).date(),
            surface=SurfaceType(tournament_data[4]),
            registration_deadline=datetime.fromisoformat(tournament_data[5]).date(),
            created=datetime.fromisoformat(tournament_data[6])
        )
        
        # Get players registered for this tournament, along with payment info
        cursor.execute(
            """
            SELECT p.name, p.created, p.phone, p.email, tp.has_paid, tp.payment_date
            FROM players p
            JOIN tournament_players tp ON p.name = tp.player_name
            WHERE tp.tournament_id = ?
            ORDER BY p.name
            LIMIT ?
            """,
            (command.tournament_id, command.limit)
        )
        player_data = cursor.fetchall()
        
        players_with_payment = []
        for row in player_data:
            player = Player(
                name=row[0],
                created=datetime.fromisoformat(row[1]),
                phone=row[2],
                email=row[3]
            )
            
            has_paid = bool(row[4])
            payment_date = datetime.fromisoformat(row[5]) if row[5] else None
            
            players_with_payment.append(
                PlayerWithPayment(
                    player=player,
                    has_paid=has_paid,
                    payment_date=payment_date
                )
            )
        
        return tournament, players_with_payment
    finally:
        conn.close()