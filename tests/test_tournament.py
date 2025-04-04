import pytest
from datetime import datetime, date, timedelta
import sqlite3

from ultimate_mcp_server.modules.data_types import (
    AddTournamentCommand, 
    ListTournamentsCommand, 
    UpdateTournamentCommand, 
    RemoveTournamentCommand,
    SurfaceType
)
from ultimate_mcp_server.modules.functionality.add_tournament import add_tournament
from ultimate_mcp_server.modules.functionality.list_tournaments import list_tournaments
from ultimate_mcp_server.modules.functionality.update_tournament import update_tournament
from ultimate_mcp_server.modules.functionality.remove_tournament import remove_tournament


def test_add_tournament(temp_db_uri):
    """Test adding a tournament."""
    # Create command to add tournament
    tournament_date = date.today() + timedelta(days=30)
    deadline = date.today() + timedelta(days=15)
    
    command = AddTournamentCommand(
        name="Test Tournament",
        location="Test Location", 
        date=tournament_date,
        surface=SurfaceType.GRASS,
        registration_deadline=deadline,
        db_uri=temp_db_uri,
    )
    
    # Add the tournament
    tournament = add_tournament(command)
    
    # Verify returned object
    assert tournament.id is not None
    assert tournament.name == "Test Tournament"
    assert tournament.location == "Test Location"
    assert tournament.date == tournament_date
    assert tournament.surface == SurfaceType.GRASS
    assert tournament.registration_deadline == deadline
    assert isinstance(tournament.created, datetime)
    
    # Verify database state
    db_path = temp_db_uri.replace('file://', '')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tournaments WHERE id = ?", (tournament.id,))
    row = cursor.fetchone()
    conn.close()
    
    assert row is not None
    assert row[1] == "Test Tournament"
    assert row[2] == "Test Location"
    assert date.fromisoformat(row[3]) == tournament_date
    assert row[4] == "grass"
    assert date.fromisoformat(row[5]) == deadline


def test_list_tournaments(temp_db_uri):
    """Test listing tournaments."""
    # Add test tournaments
    today = date.today()
    commands = [
        AddTournamentCommand(
            name=f"Test Tournament {i}",
            location=f"Location {i}",
            date=today + timedelta(days=i*10),
            surface=SurfaceType.GRASS if i % 2 == 0 else SurfaceType.BEACH,
            registration_deadline=today + timedelta(days=i*5),
            db_uri=temp_db_uri
        )
        for i in range(1, 4)  # Add 3 tournaments
    ]
    
    added_tournaments = [add_tournament(cmd) for cmd in commands]
    
    # List tournaments
    list_command = ListTournamentsCommand(db_uri=temp_db_uri)
    tournaments = list_tournaments(list_command)
    
    # Verify results
    assert len(tournaments) == 3
    
    # Check that tournaments are sorted by date
    for i in range(len(tournaments) - 1):
        assert tournaments[i].date <= tournaments[i+1].date
    
    # Verify presence of all added tournaments
    added_ids = [t.id for t in added_tournaments]
    listed_ids = [t.id for t in tournaments]
    
    for id in added_ids:
        assert id in listed_ids


def test_update_tournament(temp_db_uri):
    """Test updating a tournament."""
    # Add a test tournament
    today = date.today()
    add_command = AddTournamentCommand(
        name="Original Tournament",
        location="Original Location",
        date=today + timedelta(days=20),
        surface=SurfaceType.GRASS,
        registration_deadline=today + timedelta(days=10),
        db_uri=temp_db_uri
    )
    
    original = add_tournament(add_command)
    
    # Update the tournament - only name and surface to avoid date issues
    update_command = UpdateTournamentCommand(
        id=original.id,
        name="Updated Tournament",
        location="Updated Location",
        surface=SurfaceType.BEACH,
        db_uri=temp_db_uri
    )
    
    updated = update_tournament(update_command)
    
    # Verify returned object
    assert updated.id == original.id
    assert updated.name == "Updated Tournament"
    assert updated.location == "Updated Location"
    assert updated.date == original.date  # Should be unchanged
    assert updated.surface == SurfaceType.BEACH
    assert updated.registration_deadline == original.registration_deadline  # Unchanged
    
    # Verify database state
    db_path = temp_db_uri.replace('file://', '')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tournaments WHERE id = ?", (original.id,))
    row = cursor.fetchone()
    conn.close()
    
    assert row is not None
    assert row[1] == "Updated Tournament"
    assert row[2] == "Updated Location"
    assert date.fromisoformat(row[3]) == original.date
    assert row[4] == "beach"


def test_remove_tournament(temp_db_uri):
    """Test removing a tournament."""
    # Add a test tournament
    today = date.today()
    add_command = AddTournamentCommand(
        name="Tournament to Remove",
        location="Some Location",
        date=today + timedelta(days=20),
        surface=SurfaceType.GRASS,
        registration_deadline=today + timedelta(days=10),
        db_uri=temp_db_uri
    )
    
    tournament = add_tournament(add_command)
    
    # Remove the tournament
    remove_command = RemoveTournamentCommand(
        id=tournament.id,
        db_uri=temp_db_uri
    )
    
    result = remove_tournament(remove_command)
    
    # Verify return message
    assert "Tournament to Remove" in result
    assert "removed successfully" in result
    
    # Verify database state
    db_path = temp_db_uri.replace('file://', '')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tournaments WHERE id = ?", (tournament.id,))
    row = cursor.fetchone()
    conn.close()
    
    assert row is None  # Tournament should be gone


def test_tournament_not_found(temp_db_uri):
    """Test error when tournament not found."""
    # Try to update a non-existent tournament
    update_command = UpdateTournamentCommand(
        id=999,  # Non-existent ID
        name="Updated Name",
        db_uri=temp_db_uri
    )
    
    with pytest.raises(ValueError) as excinfo:
        update_tournament(update_command)
    
    assert "not found" in str(excinfo.value)
    
    # Try to remove a non-existent tournament
    remove_command = RemoveTournamentCommand(
        id=999,  # Non-existent ID
        db_uri=temp_db_uri
    )
    
    with pytest.raises(ValueError) as excinfo:
        remove_tournament(remove_command)
    
    assert "not found" in str(excinfo.value)