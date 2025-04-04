from datetime import datetime, date
from typing import List

from ..data_types import ListTournamentsCommand, Tournament, SurfaceType
from ..init_db import init_db
from ..utils import get_connection


def list_tournaments(command: ListTournamentsCommand) -> List[Tournament]:
    """List tournaments from the database.

    Args:
        command: The command with listing parameters

    Returns:
        List of Tournament objects sorted by date
    """
    init_db(command.db_uri)
    
    conn = get_connection(command.db_uri)
    cursor = conn.cursor()
    
    cursor.execute(
        """
        SELECT id, name, location, date, surface, registration_deadline, created 
        FROM tournaments 
        ORDER BY date ASC
        LIMIT ?
        """,
        (command.limit,)
    )
    
    results = cursor.fetchall()
    conn.close()
    
    tournaments = []
    for row in results:
        tournaments.append(
            Tournament(
                id=row[0],
                name=row[1],
                location=row[2],
                date=date.fromisoformat(row[3]),
                surface=SurfaceType(row[4]),
                registration_deadline=date.fromisoformat(row[5]),
                created=datetime.fromisoformat(row[6]),
            )
        )
    
    return tournaments