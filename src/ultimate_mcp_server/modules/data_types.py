from datetime import datetime
from pathlib import Path
from typing import Optional

from pydantic import BaseModel

from .constants import DEFAULT_DB_URI


class AddPlayerCommand(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    db_uri: str = DEFAULT_DB_URI


class ListPlayersCommand(BaseModel):
    limit: int = 1000
    db_uri: str = DEFAULT_DB_URI


class RemovePlayerCommand(BaseModel):
    name: str
    db_uri: str = DEFAULT_DB_URI


class BackupCommand(BaseModel):
    backup_path: Path
    db_uri: str = DEFAULT_DB_URI


class ImportPlayersCommand(BaseModel):
    csv_path: Path
    db_uri: str = DEFAULT_DB_URI


class Player(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    created: datetime

