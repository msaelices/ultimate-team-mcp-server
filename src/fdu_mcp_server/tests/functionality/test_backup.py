import os
import sqlite3
import tempfile
from pathlib import Path

import pytest

from ...modules.data_types import AddPlayerCommand, BackupCommand, ListPlayersCommand
from ...modules.functionality.add_player import add_player
from ...modules.functionality.backup import backup
from ...modules.functionality.list_players import list_players

def test_backup():
    # Create a temporary file for the source database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as src_temp_file:
        src_db_path = Path(src_temp_file.name)
    
    # Create a temporary file for the backup database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as backup_temp_file:
        backup_db_path = Path(backup_temp_file.name)
    
    try:
        # Add some players to the source database
        players_to_add = [
            ("Player 1", "+1111111111", "player1@example.com"),
            ("Player 2", "+2222222222", "player2@example.com"),
            ("Player 3", "+3333333333", "player3@example.com"),
        ]
        
        for name, phone, email in players_to_add:
            command = AddPlayerCommand(
                name=name,
                phone=phone,
                email=email,
                db_path=src_db_path
            )
            add_player(command)
        
        # Check that all players were added to the source database
        list_command = ListPlayersCommand(db_path=src_db_path)
        players = list_players(list_command)
        assert len(players) == 3
        
        # Remove the backup file if it exists (we want to test that the backup command creates it)
        if os.path.exists(backup_db_path):
            os.unlink(backup_db_path)
        
        # Backup the database
        backup_command = BackupCommand(
            backup_path=backup_db_path,
            db_path=src_db_path
        )
        
        result = backup(backup_command)
        
        # Check that the backup function returns a success message
        assert "Successfully backed up" in result
        
        # Check that the backup file was created
        assert os.path.exists(backup_db_path)
        
        # Connect to the backup database and check the data
        conn = sqlite3.connect(backup_db_path)
        cursor = conn.cursor()
        
        # Check that the players table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        assert 'players' in tables
        
        # Check that all players were backed up
        cursor.execute("SELECT name, phone, email FROM players;")
        backed_up_players = cursor.fetchall()
        assert len(backed_up_players) == 3
        
        # Check the data of a specific player
        player1 = next((p for p in backed_up_players if p[0] == "Player 1"), None)
        assert player1 is not None
        assert player1[1] == "+1111111111"
        assert player1[2] == "player1@example.com"
        
        conn.close()
        
        # Test backing up an empty database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as empty_src_file:
            empty_src_path = Path(empty_src_file.name)
        
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as empty_backup_file:
            empty_backup_path = Path(empty_backup_file.name)
        
        try:
            # Remove the backup file if it exists
            if os.path.exists(empty_backup_path):
                os.unlink(empty_backup_path)
            
            # Backup the empty database
            empty_backup_command = BackupCommand(
                backup_path=empty_backup_path,
                db_path=empty_src_path
            )
            
            empty_result = backup(empty_backup_command)
            
            # Check that the backup function returns a success message
            assert "Successfully backed up" in empty_result
            
            # Check that the backup file was created
            assert os.path.exists(empty_backup_path)
        
        finally:
            # Clean up the empty database files
            if os.path.exists(empty_src_path):
                os.unlink(empty_src_path)
            if os.path.exists(empty_backup_path):
                os.unlink(empty_backup_path)
    
    finally:
        # Clean up by removing the temporary database files
        if os.path.exists(src_db_path):
            os.unlink(src_db_path)
        if os.path.exists(backup_db_path):
            os.unlink(backup_db_path)