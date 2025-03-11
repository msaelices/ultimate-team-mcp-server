import os
import tempfile
from pathlib import Path

import pytest

from ...modules.data_types import AddPlayerCommand, Player
from ...modules.functionality.add_player import add_player

def test_add_player():
    # Create a temporary file for the database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_file:
        temp_db_path = Path(temp_file.name)
    
    try:
        # Create a command to add a player
        command = AddPlayerCommand(
            name="Test Player",
            phone="+1234567890",
            email="test@example.com",
            db_path=temp_db_path
        )
        
        # Add the player
        player = add_player(command)
        
        # Check that the player was added correctly
        assert player.name == "Test Player"
        assert player.phone == "+1234567890"
        assert player.email == "test@example.com"
        assert player.created is not None
        
        # Try to add the same player again (should raise an error)
        with pytest.raises(ValueError) as excinfo:
            add_player(command)
        
        assert "already exists" in str(excinfo.value)
        
        # Add a player without an email
        command2 = AddPlayerCommand(
            name="Test Player 2",
            phone="+0987654321",
            db_path=temp_db_path
        )
        
        player2 = add_player(command2)
        
        assert player2.name == "Test Player 2"
        assert player2.phone == "+0987654321"
        assert player2.email is None
        assert player2.created is not None
    
    finally:
        # Clean up by removing the temporary database file
        if os.path.exists(temp_db_path):
            os.unlink(temp_db_path)