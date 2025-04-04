import pytest
from datetime import datetime, date, timedelta
import sqlite3

from ultimate_mcp_server.modules.data_types import (
    AddPlayerCommand,
    AddTournamentCommand,
    RegisterPlayerCommand,
    MarkPaymentCommand,
    ClearPaymentCommand,
    ListTournamentPlayersCommand,
    SurfaceType
)
from ultimate_mcp_server.modules.functionality.add_player import add_player
from ultimate_mcp_server.modules.functionality.add_tournament import add_tournament
from ultimate_mcp_server.modules.functionality.register_player import register_player
from ultimate_mcp_server.modules.functionality.mark_payment import mark_payment
from ultimate_mcp_server.modules.functionality.clear_payment import clear_payment
from ultimate_mcp_server.modules.functionality.list_tournament_players import list_tournament_players


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


@pytest.fixture
def test_registration(temp_db_uri, test_player, test_tournament):
    """Register a player for a tournament."""
    command = RegisterPlayerCommand(
        tournament_id=test_tournament.id,
        player_name=test_player.name,
        db_uri=temp_db_uri
    )
    return register_player(command)


def test_mark_payment(temp_db_uri, test_player, test_tournament, test_registration):
    """Test marking a player as having paid for a tournament."""
    # Set a specific payment date
    payment_date = datetime.now()
    
    command = MarkPaymentCommand(
        tournament_id=test_tournament.id,
        player_name=test_player.name,
        payment_date=payment_date,
        db_uri=temp_db_uri
    )
    
    result = mark_payment(command)
    
    # Verify the result
    assert result.tournament_id == test_tournament.id
    assert result.player_name == test_player.name
    assert result.has_paid is True
    assert result.payment_date == payment_date
    
    # Verify database state
    db_path = temp_db_uri.replace('file://', '')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT tournament_id, player_name, has_paid, payment_date
        FROM tournament_players
        WHERE tournament_id = ? AND player_name = ?
    """, (test_tournament.id, test_player.name))
    row = cursor.fetchone()
    conn.close()
    
    assert row is not None
    assert row[0] == test_tournament.id
    assert row[1] == test_player.name
    assert bool(row[2]) is True  # has_paid should be true (1)
    assert datetime.fromisoformat(row[3]) == payment_date


def test_mark_payment_default_date(temp_db_uri, test_player, test_tournament, test_registration):
    """Test marking a player as paid without specifying a date (should use current date)."""
    command = MarkPaymentCommand(
        tournament_id=test_tournament.id,
        player_name=test_player.name,
        db_uri=temp_db_uri
    )
    
    result = mark_payment(command)
    
    # Verify the result has a payment date
    assert result.has_paid is True
    assert result.payment_date is not None
    
    # The payment date should be close to now
    time_diff = datetime.now() - result.payment_date
    assert time_diff.total_seconds() < 10  # Within 10 seconds of test execution


def test_clear_payment(temp_db_uri, test_player, test_tournament, test_registration):
    """Test clearing a player's payment status."""
    # First mark as paid
    mark_command = MarkPaymentCommand(
        tournament_id=test_tournament.id,
        player_name=test_player.name,
        db_uri=temp_db_uri
    )
    mark_payment(mark_command)
    
    # Now clear the payment
    clear_command = ClearPaymentCommand(
        tournament_id=test_tournament.id,
        player_name=test_player.name,
        db_uri=temp_db_uri
    )
    
    result = clear_payment(clear_command)
    
    # Verify the result
    assert result.tournament_id == test_tournament.id
    assert result.player_name == test_player.name
    assert result.has_paid is False
    assert result.payment_date is None
    
    # Verify database state
    db_path = temp_db_uri.replace('file://', '')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT tournament_id, player_name, has_paid, payment_date
        FROM tournament_players
        WHERE tournament_id = ? AND player_name = ?
    """, (test_tournament.id, test_player.name))
    row = cursor.fetchone()
    conn.close()
    
    assert row is not None
    assert row[0] == test_tournament.id
    assert row[1] == test_player.name
    assert bool(row[2]) is False  # has_paid should be false (0)
    assert row[3] is None  # payment_date should be NULL


def test_payment_in_listing(temp_db_uri, test_player, test_tournament, test_registration):
    """Test that payment info is included in tournament player listing."""
    # Mark as paid
    payment_date = datetime.now()
    mark_command = MarkPaymentCommand(
        tournament_id=test_tournament.id,
        player_name=test_player.name,
        payment_date=payment_date,
        db_uri=temp_db_uri
    )
    mark_payment(mark_command)
    
    # List tournament players
    list_command = ListTournamentPlayersCommand(
        tournament_id=test_tournament.id,
        db_uri=temp_db_uri
    )
    
    tournament, players = list_tournament_players(list_command)
    
    # Verify there's one player with correct payment info
    assert len(players) == 1
    assert players[0].player.name == test_player.name
    assert players[0].has_paid is True
    assert players[0].payment_date == payment_date