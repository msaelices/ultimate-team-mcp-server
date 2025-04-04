import logging
from contextlib import asynccontextmanager
from enum import Enum
from pathlib import Path
from typing import Dict, List, Any, AsyncIterator

from mcp.server.fastmcp import FastMCP, Context
from pydantic import BaseModel, Field

from .modules.data_types import (
    AddPlayerCommand,
    ListPlayersCommand,
    RemovePlayerCommand,
    BackupCommand,
    ImportPlayersCommand,
    Player,
)
from .modules.functionality.add_player import add_player
from .modules.functionality.list_players import list_players
from .modules.functionality.remove_player import remove_player
from .modules.functionality.backup import backup
from .modules.functionality.import_players import import_players
from .modules.constants import DEFAULT_DB_URI

logger = logging.getLogger(__name__)


class ServerConfig(BaseModel):
    """Server configuration."""
    db_uri: str = Field(default=DEFAULT_DB_URI, description="Database URI (sqlitecloud:// or file://)")


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
    config_model=ServerConfig
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
        name=name,
        phone=phone,
        email=email,
        db_uri=ctx.config.db_uri
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
    command = ListPlayersCommand(
        limit=limit,
        db_uri=ctx.config.db_uri
    )
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
    command = RemovePlayerCommand(
        name=name,
        db_uri=ctx.config.db_uri
    )
    remove_player(command)
    return f"Player '{name}' removed successfully"


# Add tool for backing up the database
@mcp.tool(name="backup")
def backup_tool(
    ctx: Context,
    backup_path: str = Field(..., description="Path to save the backup file"),
) -> str:
    """Backup the database to a file."""
    command = BackupCommand(
        backup_path=Path(backup_path),
        db_uri=ctx.config.db_uri
    )
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
    command = ImportPlayersCommand(
        csv_path=Path(csv_path),
        db_uri=ctx.config.db_uri
    )
    
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
    
    result.append(f"\nImport complete: {len(players)} successes, {len(errors)} failures.")
    
    return "\n".join(result)


def run_server():
    """Run the FastMCP server."""
    mcp.run()


async def serve() -> None:
    """Legacy entry point for backward compatibility."""
    # This function provides backward compatibility with the original MCP server
    logger.info("Using FastMCP server implementation")
    run_server()