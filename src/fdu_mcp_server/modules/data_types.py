from datetime import datetime
from pathlib import Path
from typing import Optional, List

from pydantic import BaseModel, Field

from .constants import DEFAULT_SQLITE_DATABASE_PATH

class AddPlayerCommand(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    db_path: Path = DEFAULT_SQLITE_DATABASE_PATH

class ListPlayersCommand(BaseModel):
    limit: int = 1000
    db_path: Path = DEFAULT_SQLITE_DATABASE_PATH

class RemovePlayerCommand(BaseModel):
    name: str
    db_path: Path = DEFAULT_SQLITE_DATABASE_PATH

class BackupCommand(BaseModel):
    backup_path: Path
    db_path: Path = DEFAULT_SQLITE_DATABASE_PATH

class ImportPlayersCommand(BaseModel):
    csv_path: Path
    db_path: Path = DEFAULT_SQLITE_DATABASE_PATH

class Player(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    created: datetime