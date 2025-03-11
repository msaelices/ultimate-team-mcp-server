import os
import sqlite3


from ultimate_mcp_server.modules.init_db import init_db


def test_init_db(temp_db_path):
    # Initialize the database
    init_db(temp_db_path)

    # Check that the database file was created
    assert os.path.exists(temp_db_path)

    # Connect to the database and check the schema
    conn = sqlite3.connect(temp_db_path)
    cursor = conn.cursor()

    # Get the list of tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]

    # Check that the players table exists
    assert "players" in tables

    # Get the schema of the players table
    cursor.execute("PRAGMA table_info(players);")
    columns = {row[1]: row[2] for row in cursor.fetchall()}

    # Check that the expected columns exist with the correct types
    assert columns["name"] == "TEXT"
    assert columns["created"] == "TIMESTAMP"
    assert columns["phone"] == "TEXT"
    assert columns["email"] == "TEXT"

    conn.close()

