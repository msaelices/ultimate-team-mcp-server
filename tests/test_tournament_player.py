import pytest
from datetime import datetime, date, timedelta
import sqlite3

from ultimate_mcp_server.modules.data_types import (
    AddPlayerCommand,
    AddTournamentCommand,
    RegisterPlayerCommand,
    UnregisterPlayerCommand,
    ListTournamentPlayersCommand,
    ListPlayerTournamentsCommand,
    SurfaceType
)
from ultimate_mcp_server.modules.functionality.add_player import add_player
from ultimate_mcp_server.modules.functionality.add_tournament import add_tournament
from ultimate_mcp_server.modules.functionality.register_player import register_player
from ultimate_mcp_server.modules.functionality.unregister_player import unregister_player
from ultimate_mcp_server.modules.functionality.list_tournament_players import list_tournament_players
from ultimate_mcp_server.modules.functionality.list_player_tournaments import list_player_tournaments


@pytest.fixture
def test_player(temp_db_uri):
    """Create a test player."""
    command = AddPlayerCommand(
        name="Test Player",
        phone="123-456-7890",
        email="test@example.com",
        db_uri=temp_db_uri
    )
    return add_player(command)


@pytest.fixture
def test_tournament(temp_db_uri):
    """Create a test tournament with future deadline."""
    today = date.today()
    command = AddTournamentCommand(
        name="Test Tournament",
        location="Test Location",
        date=today + timedelta(days=30),
        surface=SurfaceType.GRASS,
        registration_deadline=today + timedelta(days=15),
        db_uri=temp_db_uri
    )
    return add_tournament(command)


def test_register_player(temp_db_uri, test_player, test_tournament):
    """Test registering a player for a tournament."""
    command = RegisterPlayerCommand(
        tournament_id=test_tournament.id,
        player_name=test_player.name,
        db_uri=temp_db_uri
    )
    
    result = register_player(command)
    
    # Verify the registration result
    assert result.tournament_id == test_tournament.id
    assert result.player_name == test_player.name
    assert isinstance(result.registered_at, datetime)
    
    # Verify database state
    db_path = temp_db_uri.replace('file://', '')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT tournament_id, player_name FROM tournament_players
        WHERE tournament_id = ? AND player_name = ?
    """, (test_tournament.id, test_player.name))
    row = cursor.fetchone()
    conn.close()
    
    assert row is not None
    assert row[0] == test_tournament.id
    assert row[1] == test_player.name


def test_register_player_duplicate(temp_db_uri, test_player, test_tournament):
    """Test that registering a player twice raises an error."""
    # Register once
    command = RegisterPlayerCommand(
        tournament_id=test_tournament.id,
        player_name=test_player.name,
        db_uri=temp_db_uri
    )
    register_player(command)
    
    # Try to register again
    with pytest.raises(ValueError) as excinfo:
        register_player(command)
    
    assert "already registered" in str(excinfo.value)


def test_unregister_player(temp_db_uri, test_player, test_tournament):
    """Test unregistering a player from a tournament."""
    # First register the player
    register_command = RegisterPlayerCommand(
        tournament_id=test_tournament.id,
        player_name=test_player.name,
        db_uri=temp_db_uri
    )
    register_player(register_command)
    
    # Unregister the player
    unregister_command = UnregisterPlayerCommand(
        tournament_id=test_tournament.id,
        player_name=test_player.name,
        db_uri=temp_db_uri
    )
    result = unregister_player(unregister_command)
    
    # Verify the unregistration message
    assert "unregistered" in result
    assert test_player.name in result
    assert test_tournament.name in result
    
    # Verify database state
    db_path = temp_db_uri.replace('file://', '')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT tournament_id, player_name FROM tournament_players
        WHERE tournament_id = ? AND player_name = ?
    """, (test_tournament.id, test_player.name))
    row = cursor.fetchone()
    conn.close()
    
    assert row is None  # Registration record should be gone


def test_unregister_player_not_registered(temp_db_uri, test_player, test_tournament):
    """Test that unregistering a player who isn't registered raises an error."""
    command = UnregisterPlayerCommand(
        tournament_id=test_tournament.id,
        player_name=test_player.name,
        db_uri=temp_db_uri
    )
    
    with pytest.raises(ValueError) as excinfo:
        unregister_player(command)
    
    assert "not registered" in str(excinfo.value)


def test_list_tournament_players(temp_db_uri, test_player, test_tournament):
    """Test listing all players registered for a tournament."""
    # Create more players
    players = [test_player]
    for i in range(1, 3):
        command = AddPlayerCommand(
            name=f"Player {i}",
            phone=f"123-456-789{i}",
            email=f"player{i}@example.com",
            db_uri=temp_db_uri
        )
        players.append(add_player(command))
    
    # Register all players
    for player in players:
        register_command = RegisterPlayerCommand(
            tournament_id=test_tournament.id,
            player_name=player.name,
            db_uri=temp_db_uri
        )
        register_player(register_command)
    
    # List players for the tournament
    list_command = ListTournamentPlayersCommand(
        tournament_id=test_tournament.id,
        db_uri=temp_db_uri
    )
    tournament, registered_players = list_tournament_players(list_command)
    
    # Verify tournament and player count
    assert tournament.id == test_tournament.id
    assert tournament.name == test_tournament.name
    assert len(registered_players) == len(players)
    
    # Check all expected players are listed - now using PlayerWithPayment structure
    registered_names = [p.player.name for p in registered_players]
    for player in players:
        assert player.name in registered_names
        
    # Check payment status (should all be unpaid)
    for player_info in registered_players:
        assert player_info.has_paid is False
        assert player_info.payment_date is None


def test_list_player_tournaments(temp_db_uri, test_player):
    """Test listing all tournaments a player is registered for."""
    # Create multiple tournaments
    today = date.today()
    tournaments = []
    for i in range(3):
        command = AddTournamentCommand(
            name=f"Tournament {i}",
            location=f"Location {i}",
            date=today + timedelta(days=30 + i*10),
            surface=SurfaceType.GRASS if i % 2 == 0 else SurfaceType.BEACH,
            registration_deadline=today + timedelta(days=15 + i*5),
            db_uri=temp_db_uri
        )
        tournaments.append(add_tournament(command))
    
    # Register player for all tournaments
    for tournament in tournaments:
        register_command = RegisterPlayerCommand(
            tournament_id=tournament.id,
            player_name=test_player.name,
            db_uri=temp_db_uri
        )
        register_player(register_command)
    
    # List tournaments for the player
    list_command = ListPlayerTournamentsCommand(
        player_name=test_player.name,
        db_uri=temp_db_uri
    )
    player, registered_tournaments = list_player_tournaments(list_command)
    
    # Verify player and tournament count
    assert player.name == test_player.name
    assert len(registered_tournaments) == len(tournaments)
    
    # Check all expected tournaments are listed
    registered_ids = [t.id for t in registered_tournaments]
    for tournament in tournaments:
        assert tournament.id in registered_ids