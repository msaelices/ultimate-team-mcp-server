import sqlite3
from datetime import datetime
from typing import List

from ..data_types import ListPlayersCommand, Player
from ..init_db import init_db

def list_players(command: ListPlayersCommand) -> List[Player]:
    init_db(command.db_path)
    
    conn = sqlite3.connect(command.db_path)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT name, created, phone, email FROM players LIMIT ?",
        (command.limit,)
    )
    
    results = cursor.fetchall()
    conn.close()
    
    players = []
    for row in results:
        players.append(
            Player(
                name=row[0],
                created=datetime.fromisoformat(row[1]),
                phone=row[2],
                email=row[3]
            )
        )
    
    return players