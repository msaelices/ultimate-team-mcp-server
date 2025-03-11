import os
import tempfile
from pathlib import Path

import pytest

@pytest.fixture
def temp_db_uri():
    # Create a temporary file for the database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_file:
        temp_db_path = Path(temp_file.name)
        temp_db_uri = f"file://{temp_db_path.absolute()}"
    
    yield temp_db_uri
    
    # Extract the path from the URI and clean up
    db_path = temp_db_path
    if os.path.exists(db_path):
        os.unlink(db_path)