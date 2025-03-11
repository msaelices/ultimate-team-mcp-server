import os
import tempfile
from pathlib import Path

import pytest

from fdu_mcp_server.modules.data_types import AddPlayerCommand, ListPlayersCommand
from fdu_mcp_server.modules.functionality.add_player import add_player
from fdu_mcp_server.modules.functionality.list_players import list_players

def test_list_players(temp_db_path):
    # Add some players
    players_to_add = [
        ("Player 1", "+1111111111", "player1@example.com"),
        ("Player 2", "+2222222222", "player2@example.com"),
        ("Player 3", "+3333333333", "player3@example.com"),
        ("Player 4", "+4444444444", None),
        ("Player 5", "+5555555555", "player5@example.com"),
    ]
    
    for name, phone, email in players_to_add:
        command = AddPlayerCommand(
            name=name,
            phone=phone,
            email=email,
            db_path=temp_db_path
        )
        add_player(command)
    
    # Test listing all players
    list_command = ListPlayersCommand(
        db_path=temp_db_path
    )
    
    players = list_players(list_command)
    
    # Check that all players were listed
    assert len(players) == 5
    
    # Check that the players have the correct data
    player_names = [player.name for player in players]
    for name, _, _ in players_to_add:
        assert name in player_names
    
    # Check a specific player
    player3 = next(player for player in players if player.name == "Player 3")
    assert player3.phone == "+3333333333"
    assert player3.email == "player3@example.com"
    
    # Test limiting the number of players
    limit_command = ListPlayersCommand(
        limit=2,
        db_path=temp_db_path
    )
    
    limited_players = list_players(limit_command)
    
    # Check that only 2 players were listed
    assert len(limited_players) == 2
    
    # Test listing players from an empty database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as empty_temp_file:
        empty_db_path = Path(empty_temp_file.name)
    
    try:
        empty_command = ListPlayersCommand(
            db_path=empty_db_path
        )
        
        empty_players = list_players(empty_command)
        
        # Check that no players were listed
        assert len(empty_players) == 0
    finally:
        if os.path.exists(empty_db_path):
            os.unlink(empty_db_path)