import os
import sqlite3
import sqlitecloud
from pathlib import Path
from urllib.parse import urlparse
import difflib

from .constants import DEFAULT_DB_URI

def get_connection(db_uri: str = DEFAULT_DB_URI):
    """Get a database connection based on the URI scheme.
    
    Supports two URI schemes:
    - sqlitecloud:// for SQLiteCloud connections
    - file:// for local SQLite database files
    
    Args:
        db_uri: The database URI to connect to
        
    Returns:
        A database connection object
    """
    # Handle test database paths provided as strings
    if isinstance(db_uri, (str, Path)) and 'temp' in str(db_uri).lower():
        return sqlite3.connect(db_uri)
    
    # Parse the URI to determine which connection type to use
    parsed_uri = urlparse(db_uri)
    
    if parsed_uri.scheme == 'sqlitecloud':
        # SQLiteCloud connection
        return sqlitecloud.connect(db_uri)
    elif parsed_uri.scheme == 'file':
        # Local SQLite connection
        # Remove the leading '/' for Windows compatibility
        db_path = parsed_uri.path
        if os.name == 'nt' and db_path.startswith('/'):
            db_path = db_path[1:]
        return sqlite3.connect(db_path)
    else:
        # Assume it's a file path for backward compatibility
        return sqlite3.connect(db_uri)


def fuzzy_match_score(str1: str, str2: str) -> float:
    """Calculate a similarity score between two strings.
    
    Handles partial matches by checking if the first string is contained
    in the second string, in addition to using difflib for fuzzy matching.
    
    Args:
        str1: First string to compare (query)
        str2: Second string to compare (target)
        
    Returns:
        A float between 0 and 1, where 1 means perfect match
    """
    # Normalize strings for better matching
    s1 = str1.lower().strip()
    s2 = str2.lower().strip()
    
    # Check for exact match
    if s1 == s2:
        return 1.0
    
    # Check if query is a subset of the target name
    # (e.g., first name matches, or partial name matches)
    if s1 in s2:
        # Adjust score based on how much of the target is matched
        return 0.9 * (len(s1) / len(s2))
    
    # For names, also check if individual parts match
    words1 = s1.split()
    words2 = s2.split()
    
    if len(words1) == 1 and len(words2) > 1:
        # If the query is a single word, check if it matches any part of the target name
        if s1 in words2:
            return 0.85  # High score for matching a complete name part
        
        # Check for partial matches in name parts
        for word in words2:
            if s1 in word or word in s1:
                return 0.75 * (min(len(s1), len(word)) / max(len(s1), len(word)))
    
    # Use difflib's SequenceMatcher for general fuzzy matching
    return difflib.SequenceMatcher(None, s1, s2).ratio()