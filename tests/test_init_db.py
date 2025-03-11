import os
import sqlite3
from urllib.parse import urlparse


from ultimate_mcp_server.modules.init_db import init_db


def test_init_db(temp_db_uri):
    # Initialize the database
    init_db(temp_db_uri)

    # Extract the file path from the URI
    parsed_uri = urlparse(temp_db_uri)
    db_path = parsed_uri.path
    
    # For file:// URIs, path starts with /, which we need to keep on Unix
    if os.name != 'nt':  # For non-Windows platforms
        # Keep the path as is
        pass
    elif db_path.startswith('/'):  # For Windows
        db_path = db_path[1:]  # Remove leading slash for Windows compatibility
        
    # Check that the database file was created
    assert os.path.exists(db_path)

    # Connect to the database and check the schema
    conn = sqlite3.connect(db_path)
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

