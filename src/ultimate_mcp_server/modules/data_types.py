from datetime import datetime, date
from pathlib import Path
from typing import Optional, List, Literal
from enum import Enum

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


class SurfaceType(str, Enum):
    GRASS = "grass"
    BEACH = "beach"


class Tournament(BaseModel):
    id: int
    name: str
    location: str
    date: date
    surface: SurfaceType
    registration_deadline: date
    created: datetime


class AddTournamentCommand(BaseModel):
    name: str
    location: str
    date: date
    surface: SurfaceType
    registration_deadline: date
    db_uri: str = DEFAULT_DB_URI


class ListTournamentsCommand(BaseModel):
    limit: int = 1000
    db_uri: str = DEFAULT_DB_URI


class UpdateTournamentCommand(BaseModel):
    id: int
    name: Optional[str] = None
    location: Optional[str] = None
    date: Optional[date] = None
    surface: Optional[SurfaceType] = None
    registration_deadline: Optional[date] = None
    db_uri: str = DEFAULT_DB_URI


class RemoveTournamentCommand(BaseModel):
    id: int
    db_uri: str = DEFAULT_DB_URI


class TournamentPlayer(BaseModel):
    """Represents a player registered for a tournament."""
    tournament_id: int
    player_name: str
    registered_at: datetime


class RegisterPlayerCommand(BaseModel):
    """Command to register a player for a tournament."""
    tournament_id: int
    player_name: str
    db_uri: str = DEFAULT_DB_URI


class UnregisterPlayerCommand(BaseModel):
    """Command to unregister a player from a tournament."""
    tournament_id: int
    player_name: str
    db_uri: str = DEFAULT_DB_URI


class ListTournamentPlayersCommand(BaseModel):
    """Command to list all players registered for a tournament."""
    tournament_id: int
    limit: int = 1000
    db_uri: str = DEFAULT_DB_URI


class ListPlayerTournamentsCommand(BaseModel):
    """Command to list all tournaments a player is registered for."""
    player_name: str
    limit: int = 1000
    db_uri: str = DEFAULT_DB_URI

