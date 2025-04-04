from datetime import datetime
from typing import List, Tuple

from ..data_types import ListTournamentPlayersCommand, Player, Tournament
from ..utils import get_connection
from ..init_db import init_db


def list_tournament_players(command: ListTournamentPlayersCommand) -> Tuple[Tournament, List[Player]]:
    """List all players registered for a tournament.
    
    Args:
        command: The command with tournament ID and limit
        
    Returns:
        Tuple containing the tournament and a list of registered players
        
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
        
        # Get players registered for this tournament
        cursor.execute(
            """
            SELECT p.name, p.created, p.phone, p.email
            FROM players p
            JOIN tournament_players tp ON p.name = tp.player_name
            WHERE tp.tournament_id = ?
            ORDER BY p.name
            LIMIT ?
            """,
            (command.tournament_id, command.limit)
        )
        player_data = cursor.fetchall()
        
        players = []
        for row in player_data:
            players.append(
                Player(
                    name=row[0],
                    created=datetime.fromisoformat(row[1]),
                    phone=row[2],
                    email=row[3]
                )
            )
        
        return tournament, players
    finally:
        conn.close()