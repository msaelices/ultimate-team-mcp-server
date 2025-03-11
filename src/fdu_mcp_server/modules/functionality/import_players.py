import csv
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

from ..data_types import ImportPlayersCommand, Player
from ..init_db import init_db

def import_players(command: ImportPlayersCommand) -> Tuple[List[Player], List[str]]:
    """
    Import players from a CSV file, updating existing players if they already exist.
    
    Returns a tuple with:
    - List of successfully imported/updated players
    - List of error messages for failed imports
    """
    init_db(command.db_path)
    
    csv_path = Path(command.csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    conn = sqlite3.connect(command.db_path)
    cursor = conn.cursor()
    
    successful_imports = []
    errors = []
    
    with open(csv_path, 'r', newline='') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            try:
                # Normalize column names (case-insensitive, support for Spanish or English)
                name_key = next((k for k in row.keys() if k.lower() in ['name', 'nombre']), None)
                phone_key = next((k for k in row.keys() if k.lower() in ['phone', 'telefono']), None)
                email_key = next((k for k in row.keys() if k.lower() in ['email']), None)
                
                if not name_key or not phone_key:
                    errors.append(f"Row missing required fields (name and phone): {row}")
                    continue
                
                name = row[name_key].strip()
                phone = row[phone_key].strip()
                
                # Handle email - empty strings should be converted to None
                email_value = row.get(email_key, '').strip() if email_key else ''
                email = email_value if email_value else None
                
                if not name or not phone:
                    errors.append(f"Row has empty name or phone: {row}")
                    continue
                
                # Check if player already exists
                cursor.execute(
                    "SELECT name FROM players WHERE name = ?",
                    (name,)
                )
                existing = cursor.fetchone()
                
                now = datetime.now()
                
                if existing:
                    # Update existing player
                    cursor.execute(
                        "UPDATE players SET phone = ?, email = ? WHERE name = ?",
                        (phone, email, name)
                    )
                    player = Player(
                        name=name,
                        phone=phone,
                        email=email,
                        created=now  # We don't have the actual creation time
                    )
                    successful_imports.append(player)
                else:
                    # Add new player
                    cursor.execute(
                        "INSERT INTO players (name, created, phone, email) VALUES (?, ?, ?, ?)",
                        (name, now, phone, email)
                    )
                    player = Player(
                        name=name,
                        created=now,
                        phone=phone,
                        email=email
                    )
                    successful_imports.append(player)
            
            except Exception as e:
                errors.append(f"Error processing row {row}: {str(e)}")
    
    conn.commit()
    conn.close()
    
    return successful_imports, errors