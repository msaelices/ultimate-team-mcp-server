from datetime import datetime

from ..data_types import AddTournamentCommand, Tournament, SurfaceType
from ..utils import get_connection
from ..init_db import init_db


def add_tournament(command: AddTournamentCommand) -> Tournament:
    """Add a new tournament to the database.

    Args:
        command: The command containing tournament details

    Returns:
        The created Tournament object with id and created timestamp

    Raises:
        ValueError: If tournament with the same name already exists
    """
    init_db(command.db_uri)

    conn = get_connection(command.db_uri)
    cursor = conn.cursor()

    now = datetime.now()

    try:
        cursor.execute(
            """
            INSERT INTO tournaments 
            (name, location, date, surface, registration_deadline, created) 
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                command.name,
                command.location,
                command.date.isoformat(),
                command.surface.value,
                command.registration_deadline.isoformat(),
                now,
            ),
        )
        conn.commit()
        
        # Get the ID of the newly inserted row
        tournament_id = cursor.lastrowid
    except Exception as e:
        conn.rollback()
        if "UNIQUE constraint failed" in str(e) or "already exists" in str(e):
            raise ValueError(f"Tournament '{command.name}' already exists")
        raise
    finally:
        conn.close()

    return Tournament(
        id=tournament_id,
        name=command.name,
        location=command.location,
        date=command.date,
        surface=command.surface,
        registration_deadline=command.registration_deadline,
        created=now,
    )