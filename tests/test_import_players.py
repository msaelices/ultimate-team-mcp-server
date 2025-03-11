import csv
import os
import tempfile
from pathlib import Path


from ultimate_mcp_server.modules.data_types import (
    ImportPlayersCommand,
    ListPlayersCommand,
)
from ultimate_mcp_server.modules.functionality.import_players import import_players
from ultimate_mcp_server.modules.functionality.list_players import list_players


def test_import_players(temp_db_path):
    # Create a temporary CSV file
    with tempfile.NamedTemporaryFile(
        suffix=".csv", mode="w", delete=False, newline=""
    ) as csv_file:
        csv_path = Path(csv_file.name)
        writer = csv.writer(csv_file)
        writer.writerow(["Nombre", "Telefono", "Email"])
        writer.writerow(["Player 1", "+1111111111", "player1@example.com"])
        writer.writerow(["Player 2", "+2222222222", "player2@example.com"])
        writer.writerow(["Player 3", "+3333333333", ""])

    try:
        # Create the import command
        command = ImportPlayersCommand(csv_path=csv_path, db_path=temp_db_path)

        # Import the players
        players, errors = import_players(command)

        # Check that all players were imported
        assert len(players) == 3
        assert len(errors) == 0

        # Check that the players are in the database
        list_command = ListPlayersCommand(db_path=temp_db_path)
        db_players = list_players(list_command)

        assert len(db_players) == 3

        # Check a specific player
        player1 = next(player for player in db_players if player.name == "Player 1")
        assert player1.phone == "+1111111111"
        assert player1.email == "player1@example.com"

        player3 = next(player for player in db_players if player.name == "Player 3")
        assert player3.phone == "+3333333333"
        assert player3.email is None

        # Test updating existing players
        with tempfile.NamedTemporaryFile(
            suffix=".csv", mode="w", delete=False, newline=""
        ) as update_file:
            update_path = Path(update_file.name)
            writer = csv.writer(update_file)
            writer.writerow(["Nombre", "Telefono", "Email"])
            writer.writerow(
                ["Player 1", "+9999999999", "updated@example.com"]
            )  # Updated
            writer.writerow(["Player 4", "+4444444444", "player4@example.com"])  # New

        try:
            # Create the update command
            update_command = ImportPlayersCommand(
                csv_path=update_path, db_path=temp_db_path
            )

            # Import/update the players
            updated_players, update_errors = import_players(update_command)

            # Check that the players were imported/updated
            assert len(updated_players) == 2
            assert len(update_errors) == 0

            # Check that the database has the expected players
            updated_db_players = list_players(list_command)

            assert len(updated_db_players) == 4  # 3 original + 1 new

            # Check the updated player
            updated_player1 = next(
                player for player in updated_db_players if player.name == "Player 1"
            )
            assert updated_player1.phone == "+9999999999"  # Updated phone
            assert updated_player1.email == "updated@example.com"  # Updated email

            # Check the new player
            player4 = next(
                player for player in updated_db_players if player.name == "Player 4"
            )
            assert player4.phone == "+4444444444"
            assert player4.email == "player4@example.com"

        finally:
            if os.path.exists(update_path):
                os.unlink(update_path)

        # Test importing with errors
        with tempfile.NamedTemporaryFile(
            suffix=".csv", mode="w", delete=False, newline=""
        ) as error_file:
            error_path = Path(error_file.name)
            writer = csv.writer(error_file)
            writer.writerow(["Nombre", "Telefono", "Email"])
            writer.writerow(["Player 5", "+5555555555", "player5@example.com"])  # Good
            writer.writerow(["", "+6666666666", "player6@example.com"])  # Missing name
            writer.writerow(["Player 7", "", "player7@example.com"])  # Missing phone

        try:
            # Create the error command
            error_command = ImportPlayersCommand(
                csv_path=error_path, db_path=temp_db_path
            )

            # Import with errors
            error_players, error_messages = import_players(error_command)

            # Check that only valid players were imported
            assert len(error_players) == 1
            assert len(error_messages) == 2

            # Check that the database has the expected players
            final_db_players = list_players(list_command)

            assert len(final_db_players) == 5  # 4 previous + 1 new

            # Check the newly added player
            player5 = next(
                player for player in final_db_players if player.name == "Player 5"
            )
            assert player5.phone == "+5555555555"
            assert player5.email == "player5@example.com"

        finally:
            if os.path.exists(error_path):
                os.unlink(error_path)

    finally:
        if os.path.exists(csv_path):
            os.unlink(csv_path)

