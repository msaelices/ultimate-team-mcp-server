import os
import tempfile
from pathlib import Path

import pytest

@pytest.fixture
def temp_db_path():
    # Create a temporary file for the database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_file:
        temp_db_path = Path(temp_file.name)
    
    yield temp_db_path
    
    # Clean up by removing the temporary database file
    if os.path.exists(temp_db_path):
        os.unlink(temp_db_path)