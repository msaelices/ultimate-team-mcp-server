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
    has_paid: bool = False
    payment_date: Optional[datetime] = None


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


class MarkPaymentCommand(BaseModel):
    """Command to mark a player's tournament payment."""
    tournament_id: int
    player_name: str
    # If payment_date is None, current date and time will be used
    payment_date: Optional[datetime] = None
    db_uri: str = DEFAULT_DB_URI
    
    
class ClearPaymentCommand(BaseModel):
    """Command to clear a player's tournament payment."""
    tournament_id: int
    player_name: str
    db_uri: str = DEFAULT_DB_URI


class FederationPayment(BaseModel):
    """Represents a federation payment made by a player."""
    id: Optional[int] = None
    player_name: str
    payment_date: datetime
    amount: float
    notes: Optional[str] = None
    created_at: Optional[datetime] = None


class AddFederationPaymentCommand(BaseModel):
    """Command to add a federation payment for a player."""
    player_name: str
    payment_date: datetime  
    amount: float
    notes: Optional[str] = None
    db_uri: str = DEFAULT_DB_URI


class RemoveLastFederationPaymentCommand(BaseModel):
    """Command to remove the most recent federation payment for a player."""
    player_name: str
    db_uri: str = DEFAULT_DB_URI


class ListFederationPaymentsCommand(BaseModel):
    """Command to list all federation payments for a player."""
    player_name: str
    limit: int = 100
    db_uri: str = DEFAULT_DB_URI

