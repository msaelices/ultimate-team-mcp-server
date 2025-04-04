from datetime import datetime

from ..data_types import UpdateTournamentCommand, Tournament, SurfaceType
from ..utils import get_connection
from ..init_db import init_db


def update_tournament(command: UpdateTournamentCommand) -> Tournament:
    """Update an existing tournament in the database.

    Args:
        command: The command containing tournament updates

    Returns:
        The updated Tournament object

    Raises:
        ValueError: If tournament with given ID doesn't exist
    """
    init_db(command.db_uri)

    conn = get_connection(command.db_uri)
    cursor = conn.cursor()

    # First, check if the tournament exists
    cursor.execute("SELECT * FROM tournaments WHERE id = ?", (command.id,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        raise ValueError(f"Tournament with ID {command.id} not found")

    # Build current tournament object
    current = Tournament(
        id=result[0],
        name=result[1],
        location=result[2],
        date=datetime.fromisoformat(result[3]).date(),
        surface=SurfaceType(result[4]),
        registration_deadline=datetime.fromisoformat(result[5]).date(),
        created=datetime.fromisoformat(result[6]),
    )

    # Build update set and params
    updates = []
    params = []

    if command.name is not None:
        updates.append("name = ?")
        params.append(command.name)
        current.name = command.name

    if command.location is not None:
        updates.append("location = ?")
        params.append(command.location)
        current.location = command.location

    if command.date is not None:
        updates.append("date = ?")
        params.append(command.date.isoformat())
        current.date = command.date

    if command.surface is not None:
        updates.append("surface = ?")
        params.append(command.surface.value)
        current.surface = command.surface

    if command.registration_deadline is not None:
        updates.append("registration_deadline = ?")
        params.append(command.registration_deadline.isoformat())
        current.registration_deadline = command.registration_deadline

    # If no updates, return current state
    if not updates:
        conn.close()
        return current

    # Perform update
    try:
        sql = f"UPDATE tournaments SET {', '.join(updates)} WHERE id = ?"
        params.append(command.id)
        
        cursor.execute(sql, params)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        conn.close()

    return current