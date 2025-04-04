import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Dict, Any, AsyncIterator

from mcp.server.fastmcp import FastMCP, Context
from pydantic import BaseModel, Field

from .modules.data_types import (
    AddPlayerCommand,
    ListPlayersCommand,
    RemovePlayerCommand,
    BackupCommand,
    ImportPlayersCommand,
    AddTournamentCommand,
    ListTournamentsCommand,
    UpdateTournamentCommand,
    RemoveTournamentCommand,
    RegisterPlayerCommand,
    UnregisterPlayerCommand,
    ListTournamentPlayersCommand,
    ListPlayerTournamentsCommand,
    MarkPaymentCommand,
    ClearPaymentCommand,
    AddFederationPaymentCommand,
    RemoveLastFederationPaymentCommand,
    ListFederationPaymentsCommand,
    SearchPaidPlayersCommand,
    SurfaceType,
)
from .modules.functionality.add_player import add_player
from .modules.functionality.list_players import list_players
from .modules.functionality.remove_player import remove_player
from .modules.functionality.backup import backup
from .modules.functionality.import_players import import_players
from .modules.functionality.add_tournament import add_tournament
from .modules.functionality.list_tournaments import list_tournaments
from .modules.functionality.update_tournament import update_tournament
from .modules.functionality.remove_tournament import remove_tournament
from .modules.functionality.register_player import register_player
from .modules.functionality.unregister_player import unregister_player
from .modules.functionality.list_tournament_players import list_tournament_players
from .modules.functionality.list_player_tournaments import list_player_tournaments
from .modules.functionality.mark_payment import mark_payment
from .modules.functionality.clear_payment import clear_payment
from .modules.functionality.add_federation_payment import add_federation_payment
from .modules.functionality.remove_last_federation_payment import (
    remove_last_federation_payment,
)
from .modules.functionality.list_federation_payments import list_federation_payments
from .modules.functionality.search_paid_players import search_paid_players
from .modules.constants import DEFAULT_DB_URI
from datetime import date as date_type, datetime

logger = logging.getLogger(__name__)


class ServerConfig(BaseModel):
    """Server configuration."""

    db_uri: str = Field(
        default=DEFAULT_DB_URI, description="Database URI (sqlitecloud:// or file://)"
    )


# Define the server lifespan context manager
@asynccontextmanager
async def server_lifespan(mcp_server: FastMCP) -> AsyncIterator[Dict[str, Any]]:
    """Server lifespan context manager."""
    # Server startup
    logger.info("Starting Ultimate Team MCP server")

    # Return empty context - we'll pass db_uri to each tool function
    yield {}

    # Server shutdown
    logger.info("Shutting down Ultimate Team MCP server")


# Create the FastMCP server instance
mcp = FastMCP(
    "ultimate-team-mcp-server",
    description="Ultimate Frisbee Team Management MCP Server",
    lifespan=server_lifespan,
    config_model=ServerConfig,
)


# Add tool for adding a player
@mcp.tool(name="add-player")
def add_player_tool(
    ctx: Context,
    name: str = Field(..., description="Player's name"),
    phone: str = Field(..., description="Player's phone number"),
    email: str = Field(None, description="Player's email address"),
) -> str:
    """Add a new player to the database."""
    command = AddPlayerCommand(
        name=name, phone=phone, email=email, db_uri=ctx.config.db_uri
    )
    player = add_player(command)
    return f"Player '{player.name}' added successfully"


# Add tool for listing players
@mcp.tool(name="list-players")
def list_players_tool(
    ctx: Context,
    limit: int = Field(1000, description="Maximum number of players to list"),
) -> str:
    """List players in the database."""
    command = ListPlayersCommand(limit=limit, db_uri=ctx.config.db_uri)
    players = list_players(command)

    if not players:
        return "No players found"

    result = [f"Players ({len(players)}):"]
    for player in players:
        email_display = f", Email: {player.email}" if player.email else ""
        result.append(f"- {player.name} (Phone: {player.phone}{email_display})")

    return "\n".join(result)


# Add tool for removing a player
@mcp.tool(name="remove-player")
def remove_player_tool(
    ctx: Context,
    name: str = Field(..., description="Player's name to remove"),
) -> str:
    """Remove a player from the database."""
    command = RemovePlayerCommand(name=name, db_uri=ctx.config.db_uri)
    remove_player(command)
    return f"Player '{name}' removed successfully"


# Add tool for backing up the database
@mcp.tool(name="backup")
def backup_tool(
    ctx: Context,
    backup_path: str = Field(..., description="Path to save the backup file"),
) -> str:
    """Backup the database to a file."""
    command = BackupCommand(backup_path=Path(backup_path), db_uri=ctx.config.db_uri)
    result = backup(command)
    return result


# Add tool for importing players
@mcp.tool(name="import-players")
def import_players_tool(
    ctx: Context,
    csv_path: str = Field(..., description="Path to CSV file with player data"),
) -> str:
    """
    Import players from a CSV file, updating existing players.

    CSV must have headers. The following headers are recognized:
    - name/nombre: The player's name (required)
    - phone/telefono: The player's phone number (required)
    - email: The player's email address (optional)
    """
    command = ImportPlayersCommand(csv_path=Path(csv_path), db_uri=ctx.config.db_uri)

    players, errors = import_players(command)

    result = []
    if players:
        result.append(f"Successfully imported/updated {len(players)} players:")
        for player in players:
            email_display = f", Email: {player.email}" if player.email else ""
            result.append(f"- {player.name} (Phone: {player.phone}{email_display})")

    if errors:
        result.append(f"\nEncountered {len(errors)} errors:")
        for error in errors:
            result.append(f"- {error}")

    result.append(
        f"\nImport complete: {len(players)} successes, {len(errors)} failures."
    )

    return "\n".join(result)


# Tournament Management Tools


@mcp.tool(name="add-tournament")
def add_tournament_tool(
    ctx: Context,
    name: str = Field(..., description="Tournament name"),
    location: str = Field(..., description="Tournament location"),
    date: str = Field(..., description="Tournament date (YYYY-MM-DD)"),
    surface: str = Field(..., description="Surface type (grass or beach)"),
    registration_deadline: str = Field(
        ..., description="Registration deadline (YYYY-MM-DD)"
    ),
) -> str:
    """Add a new tournament to the database."""
    # Parse dates
    tournament_date = date_type.fromisoformat(date)
    deadline_date = date_type.fromisoformat(registration_deadline)

    # Validate surface type
    surface_type = SurfaceType(surface.lower())

    command = AddTournamentCommand(
        name=name,
        location=location,
        date=tournament_date,
        surface=surface_type,
        registration_deadline=deadline_date,
        db_uri=ctx.config.db_uri,
    )

    result = add_tournament(command)
    return f"Added tournament: {result.name} (ID: {result.id})"


@mcp.tool(name="list-tournaments")
def list_tournaments_tool(
    ctx: Context,
    limit: int = Field(1000, description="Maximum number of tournaments to list"),
) -> str:
    """List tournaments in the database."""
    command = ListTournamentsCommand(limit=limit, db_uri=ctx.config.db_uri)

    tournaments = list_tournaments(command)

    if not tournaments:
        return "No tournaments found"

    result = [f"Tournaments ({len(tournaments)}):"]
    for tournament in tournaments:
        result.append(f"- ID: {tournament.id}, Name: {tournament.name}")
        result.append(f"  Location: {tournament.location}")
        result.append(f"  Date: {tournament.date}")
        result.append(f"  Surface: {tournament.surface.value}")
        result.append(f"  Registration Deadline: {tournament.registration_deadline}")
        result.append("")

    return "\n".join(result)


@mcp.tool(name="update-tournament")
def update_tournament_tool(
    ctx: Context,
    id: int = Field(..., description="Tournament ID"),
    name: str = Field(None, description="Tournament name"),
    location: str = Field(None, description="Tournament location"),
    date: str = Field(None, description="Tournament date (YYYY-MM-DD)"),
    surface: str = Field(None, description="Surface type (grass or beach)"),
    registration_deadline: str = Field(
        None, description="Registration deadline (YYYY-MM-DD)"
    ),
) -> str:
    """Update an existing tournament."""
    # Parse dates if provided
    tournament_date = date_type.fromisoformat(date) if date else None
    deadline_date = (
        date_type.fromisoformat(registration_deadline)
        if registration_deadline
        else None
    )

    # Parse surface type if provided
    surface_type = SurfaceType(surface.lower()) if surface else None

    # Check if any fields were provided to update
    if all(v is None for v in [name, location, date, surface, registration_deadline]):
        return "Error: At least one field must be specified to update."

    command = UpdateTournamentCommand(
        id=id,
        name=name,
        location=location,
        date=tournament_date,
        surface=surface_type,
        registration_deadline=deadline_date,
        db_uri=ctx.config.db_uri,
    )

    result = update_tournament(command)
    return f"Updated tournament: {result.name} (ID: {result.id})"


@mcp.tool(name="remove-tournament")
def remove_tournament_tool(
    ctx: Context,
    id: int = Field(..., description="Tournament ID to remove"),
) -> str:
    """Remove a tournament from the database."""
    command = RemoveTournamentCommand(id=id, db_uri=ctx.config.db_uri)

    result = remove_tournament(command)
    return result


# Tournament Registration Tools


@mcp.tool(name="register-player")
def register_player_tool(
    ctx: Context,
    tournament_id: int = Field(..., description="Tournament ID"),
    player_name: str = Field(..., description="Name of the player to register"),
) -> str:
    """Register a player for a tournament."""
    command = RegisterPlayerCommand(
        tournament_id=tournament_id, player_name=player_name, db_uri=ctx.config.db_uri
    )

    result = register_player(command)
    return f"Player '{result.player_name}' registered for tournament ID {result.tournament_id}"


@mcp.tool(name="unregister-player")
def unregister_player_tool(
    ctx: Context,
    tournament_id: int = Field(..., description="Tournament ID"),
    player_name: str = Field(..., description="Name of the player to unregister"),
) -> str:
    """Unregister a player from a tournament."""
    command = UnregisterPlayerCommand(
        tournament_id=tournament_id, player_name=player_name, db_uri=ctx.config.db_uri
    )

    result = unregister_player(command)
    return result


@mcp.tool(name="list-tournament-players")
def list_tournament_players_tool(
    ctx: Context,
    tournament_id: int = Field(..., description="Tournament ID"),
    limit: int = Field(1000, description="Maximum number of players to list"),
) -> str:
    """List all players registered for a tournament."""
    command = ListTournamentPlayersCommand(
        tournament_id=tournament_id, limit=limit, db_uri=ctx.config.db_uri
    )

    tournament, players = list_tournament_players(command)

    result = [f"Tournament: {tournament.name} (ID: {tournament.id})"]
    result.append(f"Location: {tournament.location}")
    result.append(f"Date: {tournament.date}")
    result.append(f"Surface: {tournament.surface.value}")

    if not players:
        result.append("\nNo players registered for this tournament")
        return "\n".join(result)

    # Print registered players with payment info
    result.append(f"\nRegistered Players ({len(players)}):")
    for player_info in players:
        player = player_info.player
        email_display = f", Email: {player.email}" if player.email else ""
        payment_status = "[PAID]" if player_info.has_paid else "[UNPAID]"
        payment_date = (
            f" on {player_info.payment_date.strftime('%Y-%m-%d')}"
            if player_info.payment_date
            else ""
        )

        result.append(f"- {player.name} {payment_status}{payment_date}")
        result.append(f"  Phone: {player.phone}{email_display}")

    return "\n".join(result)


@mcp.tool(name="list-player-tournaments")
def list_player_tournaments_tool(
    ctx: Context,
    player_name: str = Field(..., description="Name of the player"),
    limit: int = Field(1000, description="Maximum number of tournaments to list"),
) -> str:
    """List all tournaments a player is registered for."""
    command = ListPlayerTournamentsCommand(
        player_name=player_name, limit=limit, db_uri=ctx.config.db_uri
    )

    player, tournaments = list_player_tournaments(command)

    result = [f"Player: {player.name}"]
    result.append(f"Phone: {player.phone}")
    if player.email:
        result.append(f"Email: {player.email}")

    if not tournaments:
        result.append("\nPlayer is not registered for any tournaments")
        return "\n".join(result)

    result.append(f"\nRegistered Tournaments ({len(tournaments)}):")
    for tournament in tournaments:
        result.append(f"- ID: {tournament.id}, Name: {tournament.name}")
        result.append(f"  Date: {tournament.date}, Location: {tournament.location}")
        result.append(f"  Surface: {tournament.surface.value}")
        result.append("")

    return "\n".join(result)


# Tournament Payment Tools


@mcp.tool(name="mark-payment")
def mark_payment_tool(
    ctx: Context,
    tournament_id: int = Field(..., description="Tournament ID"),
    player_name: str = Field(..., description="Name of the player"),
    payment_date: str = Field(
        None, description="Payment date (YYYY-MM-DD), defaults to today"
    ),
) -> str:
    """Mark a player as having paid for a tournament."""
    # Parse payment date if provided, otherwise use current date/time
    payment_datetime = None
    if payment_date:
        date_obj = date_type.fromisoformat(payment_date)
        payment_datetime = datetime.combine(
            date_obj, datetime.min.time().replace(hour=12)
        )

    command = MarkPaymentCommand(
        tournament_id=tournament_id,
        player_name=player_name,
        payment_date=payment_datetime,
        db_uri=ctx.config.db_uri,
    )

    result = mark_payment(command)

    payment_date_str = result.payment_date.strftime("%Y-%m-%d %H:%M")
    return f"Player '{result.player_name}' marked as paid for tournament ID {result.tournament_id}\nPayment date: {payment_date_str}"


@mcp.tool(name="clear-payment")
def clear_payment_tool(
    ctx: Context,
    tournament_id: int = Field(..., description="Tournament ID"),
    player_name: str = Field(..., description="Name of the player"),
) -> str:
    """Clear a player's payment status for a tournament."""
    command = ClearPaymentCommand(
        tournament_id=tournament_id,
        player_name=player_name,
        db_uri=ctx.config.db_uri,
    )

    result = clear_payment(command)
    return f"Payment status cleared for player '{result.player_name}' in tournament ID {result.tournament_id}"


@mcp.tool(name="search-paid-players")
def search_paid_players_tool(
    ctx: Context,
    tournament_id: int = Field(..., description="Tournament ID"),
    name: str = Field("", description="Name to search for (fuzzy matching)"),
    threshold: float = Field(
        0.6, description="Match threshold (0-1), higher = stricter matching"
    ),
    limit: int = Field(100, description="Maximum number of results"),
) -> str:
    """Search for players who have paid for a tournament, with fuzzy name matching."""
    command = SearchPaidPlayersCommand(
        tournament_id=tournament_id,
        name_query=name,
        match_threshold=threshold,
        limit=limit,
        db_uri=ctx.config.db_uri,
    )

    tournament, players = search_paid_players(command)

    result = [f"Tournament: {tournament.name} (ID: {tournament.id})"]
    result.append(f"Location: {tournament.location}")
    result.append(f"Date: {tournament.date}")

    if not players:
        if name:
            result.append(
                f"\nNo players matching '{name}' found who have paid for this tournament"
            )
        else:
            result.append("\nNo players have paid for this tournament")
        return "\n".join(result)

    # Print matching players
    if name:
        result.append(f"\nPlayers matching '{name}' who have paid ({len(players)}):")
    else:
        result.append(f"\nPlayers who have paid ({len(players)}):")

    for player_info in players:
        player = player_info.player
        email_display = f", Email: {player.email}" if player.email else ""
        payment_date = player_info.payment_date.strftime("%Y-%m-%d")

        # Show match score if searching
        match_display = ""
        if name:
            match_percentage = int(player_info.match_score * 100)
            match_display = f" (Match: {match_percentage}%)"

        result.append(f"- {player.name}{match_display}")
        result.append(f"  Phone: {player.phone}{email_display}")
        result.append(f"  Paid on: {payment_date}")
        result.append("")

    return "\n".join(result)


# Federation Payment Tools


@mcp.tool(name="add-federation-payment")
def add_federation_payment_tool(
    ctx: Context,
    player_name: str = Field(..., description="Name of the player"),
    amount: float = Field(..., description="Payment amount"),
    payment_date: str = Field(
        None, description="Payment date (YYYY-MM-DD), defaults to today"
    ),
    notes: str = Field(None, description="Optional notes about the payment"),
) -> str:
    """Add a federation payment for a player."""
    # Parse payment date
    if payment_date:
        date_obj = date_type.fromisoformat(payment_date)
        payment_datetime = datetime.combine(
            date_obj, datetime.min.time().replace(hour=12)
        )
    else:
        payment_datetime = datetime.now()

    command = AddFederationPaymentCommand(
        player_name=player_name,
        payment_date=payment_datetime,
        amount=amount,
        notes=notes,
        db_uri=ctx.config.db_uri,
    )

    result = add_federation_payment(command)

    output = [f"Federation payment added for player '{result.player_name}'"]
    output.append(f"Payment ID: {result.id}")
    output.append(f"Amount: {result.amount}")
    output.append(f"Date: {result.payment_date.strftime('%Y-%m-%d')}")
    if result.notes:
        output.append(f"Notes: {result.notes}")

    return "\n".join(output)


@mcp.tool(name="remove-last-federation-payment")
def remove_last_federation_payment_tool(
    ctx: Context,
    player_name: str = Field(..., description="Name of the player"),
) -> str:
    """Remove the most recent federation payment for a player."""
    command = RemoveLastFederationPaymentCommand(
        player_name=player_name, db_uri=ctx.config.db_uri
    )

    result = remove_last_federation_payment(command)

    if result:
        output = [f"Removed federation payment for player '{result.player_name}'"]
        output.append(f"Payment ID: {result.id}")
        output.append(f"Amount: {result.amount}")
        output.append(f"Date: {result.payment_date.strftime('%Y-%m-%d')}")
        if result.notes:
            output.append(f"Notes: {result.notes}")
        return "\n".join(output)
    else:
        return f"No federation payments found for player '{player_name}'"


@mcp.tool(name="list-federation-payments")
def list_federation_payments_tool(
    ctx: Context,
    player_name: str = Field(..., description="Name of the player"),
    limit: int = Field(100, description="Maximum number of payments to list"),
) -> str:
    """List all federation payments for a player."""
    command = ListFederationPaymentsCommand(
        player_name=player_name, limit=limit, db_uri=ctx.config.db_uri
    )

    player, payments = list_federation_payments(command)

    output = [f"Player: {player.name}"]
    output.append(f"Phone: {player.phone}")
    if player.email:
        output.append(f"Email: {player.email}")

    if not payments:
        output.append("\nNo federation payments found for this player")
        return "\n".join(output)

    # Print federation payments
    output.append(f"\nFederation Payments ({len(payments)}):")

    # Calculate total
    total_amount = sum(payment.amount for payment in payments)

    for payment in payments:
        output.append(
            f"- ID: {payment.id}, Date: {payment.payment_date.strftime('%Y-%m-%d')}"
        )
        output.append(f"  Amount: {payment.amount:.2f}")
        if payment.notes:
            output.append(f"  Notes: {payment.notes}")

    output.append(f"\nTotal Payments: {total_amount:.2f}")
    return "\n".join(output)


def run_server():
    """Run the FastMCP server."""
    mcp.run()


async def serve() -> None:
    """Legacy entry point for backward compatibility."""
    # This function provides backward compatibility with the original MCP server
    logger.info("Using FastMCP server implementation")
    run_server()

