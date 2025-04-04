from datetime import datetime
from typing import List, Tuple, Dict
from dataclasses import dataclass

from ..data_types import SearchPaidPlayersCommand, Player, Tournament, SurfaceType
from ..utils import get_connection, fuzzy_match_score
from ..init_db import init_db


@dataclass
class PlayerPaymentInfo:
    """Class to hold player and payment information."""
    player: Player
    payment_date: datetime
    match_score: float = 1.0  # Default is perfect match


def search_paid_players(command: SearchPaidPlayersCommand) -> Tuple[Tournament, List[PlayerPaymentInfo]]:
    """Search for players who have paid for a specific tournament.
    
    Uses fuzzy matching on player names if a search query is provided.
    
    Args:
        command: The search command with tournament ID and optional name query
        
    Returns:
        Tuple containing the tournament and a list of players who have paid
        
    Raises:
        ValueError: If the tournament doesn't exist
    """
    init_db(command.db_uri)
    
    conn = get_connection(command.db_uri)
    cursor = conn.cursor()
    
    try:
        # First, get tournament details
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
        
        # Create Tournament object
        tournament = Tournament(
            id=tournament_data[0],
            name=tournament_data[1],
            location=tournament_data[2],
            date=datetime.fromisoformat(tournament_data[3]).date(),
            surface=SurfaceType(tournament_data[4]),
            registration_deadline=datetime.fromisoformat(tournament_data[5]).date(),
            created=datetime.fromisoformat(tournament_data[6])
        )
        
        # Get players who have paid for this tournament
        cursor.execute(
            """
            SELECT p.name, p.created, p.phone, p.email, tp.payment_date
            FROM players p
            JOIN tournament_players tp ON p.name = tp.player_name
            WHERE tp.tournament_id = ? AND tp.has_paid = 1
            ORDER BY p.name
            """,
            (command.tournament_id,)
        )
        player_data = cursor.fetchall()
        
        # If no players have paid, return empty list
        if not player_data:
            return tournament, []
        
        # Process all players
        all_players = []
        for row in player_data:
            player = Player(
                name=row[0],
                created=datetime.fromisoformat(row[1]),
                phone=row[2],
                email=row[3]
            )
            payment_date = datetime.fromisoformat(row[4])
            
            # Only add the player if no search query or they match the search
            if not command.name_query:
                # No search, add all players
                all_players.append(PlayerPaymentInfo(
                    player=player,
                    payment_date=payment_date
                ))
            else:
                # Try various matching strategies
                match_score = 0.0
                
                # 1. Full name match
                name_match = fuzzy_match_score(command.name_query, player.name)
                match_score = max(match_score, name_match)
                
                # 2. Check against name parts separately
                name_parts = player.name.split()
                for part in name_parts:
                    part_match = fuzzy_match_score(command.name_query, part)
                    match_score = max(match_score, part_match)
                
                # 3. Special case for first name searching
                if len(command.name_query.split()) == 1 and command.name_query.lower() == name_parts[0].lower():
                    match_score = max(match_score, 0.9)  # High score for first name match
                
                # Include player if they meet the threshold
                if match_score >= command.match_threshold:
                    all_players.append(PlayerPaymentInfo(
                        player=player,
                        payment_date=payment_date,
                        match_score=match_score
                    ))
        
        # Sort by match score (highest first), then by name
        if command.name_query:
            all_players.sort(key=lambda p: (-p.match_score, p.player.name))
        
        # Apply limit
        return tournament, all_players[:command.limit]
    finally:
        conn.close()