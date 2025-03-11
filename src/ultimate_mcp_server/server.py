import logging
from enum import Enum
from pathlib import Path
from typing import Dict, List, Any

from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

from .modules.data_types import (
    AddPlayerCommand,
    ListPlayersCommand,
    RemovePlayerCommand,
    BackupCommand,
    ImportPlayersCommand,
)
from .modules.functionality.add_player import add_player
from .modules.functionality.list_players import list_players
from .modules.functionality.remove_player import remove_player
from .modules.functionality.backup import backup
from .modules.functionality.import_players import import_players

logger = logging.getLogger(__name__)


class FduTools(str, Enum):
    """FDU MCP tools."""

    ADD_PLAYER = "add-player"
    IMPORT_PLAYERS = "import-players"
    LIST_PLAYERS = "list-players"
    REMOVE_PLAYER = "remove-player"
    BACKUP = "backup"


async def serve() -> None:
    logger.info("Starting FDU MCP server")

    server = Server("ultimate-team-mcp-server")

    @server.list_tools()
    async def list_tools() -> List[Dict[str, Any]]:
        return [
            Tool(
                name=FduTools.ADD_PLAYER,
                description="Add a new player to the database",
                inputSchema=AddPlayerCommand.model_json_schema(),
            ),
            Tool(
                name=FduTools.LIST_PLAYERS,
                description="List players in the database",
                inputSchema=ListPlayersCommand.model_json_schema(),
            ),
            Tool(
                name=FduTools.REMOVE_PLAYER,
                description="Remove a player from the database",
                inputSchema=RemovePlayerCommand.model_json_schema(),
            ),
            Tool(
                name=FduTools.BACKUP,
                description="Backup the database to a file",
                inputSchema=BackupCommand.model_json_schema(),
            ),
            Tool(
                name=FduTools.IMPORT_PLAYERS,
                description="Import players from a CSV file, updating existing players",
                inputSchema=ImportPlayersCommand.model_json_schema(),
            ),
        ]

    @server.call_tool()
    async def call_tool(tool_name: str, parameters: dict) -> list[TextContent]:
        if tool_name == "add-player":
            command = AddPlayerCommand(
                name=parameters["name"],
                phone=parameters["phone"],
                email=parameters.get("email"),
            )
            player = add_player(command)
            return [
                TextContent(
                    type="text",
                    text=f"Player '{player.name}' added successfully",
                ),
            ]

        elif tool_name == "list-players":
            command = ListPlayersCommand(
                limit=parameters.get("limit", 1000),
            )
            players = list_players(command)
            return [
                TextContent(
                    type="text",
                    text=f"Players ({len(players)}):",
                ),
                *[
                    TextContent(
                        type="text",
                        text=f"- {player.name} (Phone: {player.phone}, Email: {player.email})",
                    )
                    for player in players
                ],
            ]

        elif tool_name == "remove-player":
            command = RemovePlayerCommand(
                name=parameters["name"],
            )
            remove_player(command)
            return [
                TextContent(
                    type="text",
                    text=f"Player '{parameters['name']}' removed successfully",
                ),
            ]

        elif tool_name == "backup":
            command = BackupCommand(
                backup_path=Path(parameters["backup_path"]),
            )
            result = backup(command)
            return [
                TextContent(
                    type="text",
                    text=result,
                ),
            ]

        elif tool_name == "import-players":
            command = ImportPlayersCommand(
                csv_path=Path(parameters["csv_path"]),
            )
            players, errors = import_players(command)
            return [
                TextContent(
                    type="text", text=f"Success: {len(players)} players imported"
                ),
            ]
        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    # Run the server
    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)
