import pytest

from ultimate_mcp_server.modules.data_types import (
    AddPlayerCommand,
    RemovePlayerCommand,
    ListPlayersCommand,
)
from ultimate_mcp_server.modules.functionality.add_player import add_player
from ultimate_mcp_server.modules.functionality.remove_player import remove_player
from ultimate_mcp_server.modules.functionality.list_players import list_players


def test_remove_player(temp_db_path):
    # Add some players
    players_to_add = [
        ("Player 1", "+1111111111", "player1@example.com"),
        ("Player 2", "+2222222222", "player2@example.com"),
        ("Player 3", "+3333333333", "player3@example.com"),
    ]

    for name, phone, email in players_to_add:
        command = AddPlayerCommand(
            name=name, phone=phone, email=email, db_path=temp_db_path
        )
        add_player(command)

    # Check that all players were added
    list_command = ListPlayersCommand(db_path=temp_db_path)
    players = list_players(list_command)
    assert len(players) == 3

    # Remove a player
    remove_command = RemovePlayerCommand(name="Player 2", db_path=temp_db_path)

    # Check that the remove function returns True
    assert remove_player(remove_command) is True

    # Check that the player was removed
    players = list_players(list_command)
    assert len(players) == 2
    player_names = [player.name for player in players]
    assert "Player 2" not in player_names
    assert "Player 1" in player_names
    assert "Player 3" in player_names

    # Try to remove a player that doesn't exist
    with pytest.raises(ValueError) as excinfo:
        remove_command = RemovePlayerCommand(
            name="Non-existent Player", db_path=temp_db_path
        )
        remove_player(remove_command)

    assert "not found" in str(excinfo.value)

    # Check that the existing players are still there
    players = list_players(list_command)
    assert len(players) == 2

