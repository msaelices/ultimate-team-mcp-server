import pytest
from datetime import datetime, date, timedelta

from ultimate_mcp_server.modules.data_types import (
    AddPlayerCommand,
    AddTournamentCommand,
    RegisterPlayerCommand,
    MarkPaymentCommand,
    SearchPaidPlayersCommand,
    SurfaceType
)
from ultimate_mcp_server.modules.functionality.add_player import add_player
from ultimate_mcp_server.modules.functionality.add_tournament import add_tournament
from ultimate_mcp_server.modules.functionality.register_player import register_player
from ultimate_mcp_server.modules.functionality.mark_payment import mark_payment
from ultimate_mcp_server.modules.functionality.search_paid_players import search_paid_players
from ultimate_mcp_server.modules.utils import fuzzy_match_score


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
def test_players(temp_db_uri):
    """Create a set of test players with varying names."""
    player_names = [
        "Juan García",
        "María Rodríguez",
        "Pedro López",
        "Ana Martínez",
        "Carlos Sánchez",
        "Laura González"
    ]
    
    players = []
    for i, name in enumerate(player_names):
        command = AddPlayerCommand(
            name=name,
            phone=f"123-456-{7890+i}",
            email=f"player{i}@example.com",
            db_uri=temp_db_uri
        )
        players.append(add_player(command))
    
    return players


@pytest.fixture
def paid_players(temp_db_uri, test_tournament, test_players):
    """Register and mark some players as paid."""
    # Register all players
    for player in test_players:
        register_command = RegisterPlayerCommand(
            tournament_id=test_tournament.id,
            player_name=player.name,
            db_uri=temp_db_uri
        )
        register_player(register_command)
    
    # Mark only the first 3 players as paid
    paid_players = []
    for i in range(3):
        mark_command = MarkPaymentCommand(
            tournament_id=test_tournament.id,
            player_name=test_players[i].name,
            db_uri=temp_db_uri
        )
        paid_players.append(mark_payment(mark_command))
    
    return paid_players


def test_fuzzy_match_score():
    """Test the fuzzy matching utility function."""
    # Exact matches
    assert fuzzy_match_score("test", "test") == 1.0
    assert fuzzy_match_score("Juan", "Juan") == 1.0
    
    # Case insensitive matches
    assert fuzzy_match_score("test", "TEST") == 1.0
    assert fuzzy_match_score("Juan", "JUAN") == 1.0
    
    # Whitespace handling
    assert fuzzy_match_score("Juan García", "Juan García") == 1.0
    assert fuzzy_match_score(" Juan ", "Juan") == 1.0
    
    # Similar but not exact matches
    assert 0.7 < fuzzy_match_score("Juan", "Jaun") < 1.0  # Typo
    assert 0.7 < fuzzy_match_score("García", "Garcia") < 1.0  # Missing accent
    assert 0.7 < fuzzy_match_score("Juan García", "Juan Garcia") < 1.0
    
    # Less similar matches
    assert 0.5 < fuzzy_match_score("Juan", "Juana") < 0.9
    
    # Very different strings
    assert fuzzy_match_score("Juan", "Pedro") < 0.5


def test_search_all_paid_players(temp_db_uri, test_tournament, test_players, paid_players):
    """Test searching all paid players (no specific name query)."""
    command = SearchPaidPlayersCommand(
        tournament_id=test_tournament.id,
        db_uri=temp_db_uri
    )
    
    tournament, results = search_paid_players(command)
    
    # Verify tournament
    assert tournament.id == test_tournament.id
    assert tournament.name == test_tournament.name
    
    # Should return only the 3 paid players
    assert len(results) == 3
    
    # Check all expected players are in results
    result_names = [r.player.name for r in results]
    for i in range(3):
        assert test_players[i].name in result_names


def test_search_paid_players_exact_match(temp_db_uri, test_tournament, test_players, paid_players):
    """Test searching for a paid player by exact name."""
    # Search for the first player (who has paid)
    command = SearchPaidPlayersCommand(
        tournament_id=test_tournament.id,
        name_query=test_players[0].name,
        db_uri=temp_db_uri
    )
    
    _, results = search_paid_players(command)
    
    # Should find exactly one match
    assert len(results) == 1
    assert results[0].player.name == test_players[0].name
    assert results[0].match_score == 1.0  # Perfect match
    
    # Search for a player who hasn't paid - should find none
    command = SearchPaidPlayersCommand(
        tournament_id=test_tournament.id,
        name_query=test_players[4].name,  # Fifth player hasn't paid
        db_uri=temp_db_uri
    )
    
    _, results = search_paid_players(command)
    assert len(results) == 0


def test_search_paid_players_fuzzy_match(temp_db_uri, test_tournament, test_players, paid_players):
    """Test searching for a paid player with fuzzy name matching."""
    # Search with a typo
    if test_players[0].name.startswith("Juan"):
        fuzzy_name = "Jaun Garcia"  # Typo in first name
    else:
        # Create a common typo in the name
        name_parts = test_players[0].name.split()
        if len(name_parts) >= 2:
            fuzzy_name = f"{name_parts[0][:-1]}{name_parts[0][-1].swapcase()} {name_parts[1]}"
        else:
            fuzzy_name = name_parts[0][:-1] + name_parts[0][-1].swapcase()
    
    # Search with fuzzy name
    command = SearchPaidPlayersCommand(
        tournament_id=test_tournament.id,
        name_query=fuzzy_name,
        match_threshold=0.6,  # Lower threshold to allow more fuzzy matches
        db_uri=temp_db_uri
    )
    
    _, results = search_paid_players(command)
    
    # Should find at least one match
    assert len(results) > 0
    
    # First result should be the closest match
    closest_match = results[0].player.name
    closest_match_score = results[0].match_score
    
    # Score should be high but not perfect
    assert 0.6 <= closest_match_score < 1.0
    
    # With very strict threshold, should find fewer or no matches
    strict_command = SearchPaidPlayersCommand(
        tournament_id=test_tournament.id,
        name_query=fuzzy_name,
        match_threshold=0.9,  # Very high threshold
        db_uri=temp_db_uri
    )
    
    _, strict_results = search_paid_players(strict_command)
    assert len(strict_results) <= len(results)


def test_search_paid_players_partial_name(temp_db_uri, test_tournament, test_players, paid_players):
    """Test searching with just part of a name."""
    # Get first name of a paid player and ensure they're actually paid
    paid_name = test_players[0].name
    first_name = paid_name.split()[0]
    
    # Use a low threshold to ensure we get matches
    command = SearchPaidPlayersCommand(
        tournament_id=test_tournament.id,
        name_query=first_name,
        match_threshold=0.4,  # Lower threshold to catch partial names
        db_uri=temp_db_uri
    )
    
    _, results = search_paid_players(command)
    
    # We should find at least one match with the lower threshold
    assert len(results) >= 1
    assert any(paid_name == r.player.name for r in results)


def test_tournament_not_found(temp_db_uri):
    """Test error when tournament not found."""
    command = SearchPaidPlayersCommand(
        tournament_id=999,  # Non-existent ID
        db_uri=temp_db_uri
    )
    
    with pytest.raises(ValueError) as excinfo:
        search_paid_players(command)
    
    assert "not found" in str(excinfo.value)