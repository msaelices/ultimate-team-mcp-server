from datetime import datetime
from typing import Tuple, List

from ..data_types import ListPlayerTournamentsCommand, Player, Tournament, SurfaceType
from ..utils import get_connection
from ..init_db import init_db


def list_player_tournaments(command: ListPlayerTournamentsCommand) -> Tuple[Player, List[Tournament]]:
    """List all tournaments a player is registered for.
    
    Args:
        command: The command with player name and limit
        
    Returns:
        Tuple containing the player and a list of tournaments they're registered for
        
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
        
        player = Player(
            name=player_data[0],
            created=datetime.fromisoformat(player_data[1]),
            phone=player_data[2],
            email=player_data[3]
        )
        
        # Get tournaments this player is registered for
        cursor.execute(
            """
            SELECT t.id, t.name, t.location, t.date, t.surface, 
                   t.registration_deadline, t.created
            FROM tournaments t
            JOIN tournament_players tp ON t.id = tp.tournament_id
            WHERE tp.player_name = ?
            ORDER BY t.date
            LIMIT ?
            """,
            (command.player_name, command.limit)
        )
        tournament_data = cursor.fetchall()
        
        tournaments = []
        for row in tournament_data:
            tournaments.append(
                Tournament(
                    id=row[0],
                    name=row[1],
                    location=row[2],
                    date=datetime.fromisoformat(row[3]).date(),
                    surface=SurfaceType(row[4]),
                    registration_deadline=datetime.fromisoformat(row[5]).date(),
                    created=datetime.fromisoformat(row[6])
                )
            )
        
        return player, tournaments
    finally:
        conn.close()