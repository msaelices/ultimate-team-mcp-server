import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from mcp.server import Server

from .modules.data_types import (
    AddPlayerCommand,
    ListPlayersCommand,
    RemovePlayerCommand,
    BackupCommand,
    Player
)
from .modules.functionality.add_player import add_player
from .modules.functionality.list_players import list_players
from .modules.functionality.remove_player import remove_player
from .modules.functionality.backup import backup
from .modules.constants import DEFAULT_SQLITE_DATABASE_PATH

server = Server("fdu")

def serve(sqlite_database: Optional[Path] = None) -> None:
    @server.list_tools()
    def list_tools() -> List[Dict[str, Any]]:
        return [
            {
                "name": "add-player",
                "description": "Add a new player to the database",
                "parameter_schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "phone": {"type": "string"},
                        "email": {"type": "string", "optional": True},
                    },
                    "required": ["name", "phone"]
                }
            },
            {
                "name": "list-players",
                "description": "List players in the database",
                "parameter_schema": {
                    "type": "object",
                    "properties": {
                        "limit": {"type": "number", "optional": True}
                    }
                }
            },
            {
                "name": "remove-player",
                "description": "Remove a player from the database",
                "parameter_schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"}
                    },
                    "required": ["name"]
                }
            },
            {
                "name": "backup",
                "description": "Backup the database to a file",
                "parameter_schema": {
                    "type": "object",
                    "properties": {
                        "backup_path": {"type": "string"}
                    },
                    "required": ["backup_path"]
                }
            }
        ]

    @server.call_tool()
    def call_tool(tool_name: str, parameters: Dict[str, Any]) -> Union[Dict[str, Any], List[Dict[str, Any]], str]:
        db_path = sqlite_database or DEFAULT_SQLITE_DATABASE_PATH
        
        if tool_name == "add-player":
            command = AddPlayerCommand(
                name=parameters["name"],
                phone=parameters["phone"],
                email=parameters.get("email"),
                db_path=db_path
            )
            player = add_player(command)
            return player.model_dump()
        
        elif tool_name == "list-players":
            command = ListPlayersCommand(
                limit=parameters.get("limit", 1000),
                db_path=db_path
            )
            players = list_players(command)
            return [player.model_dump() for player in players]
        
        elif tool_name == "remove-player":
            command = RemovePlayerCommand(
                name=parameters["name"],
                db_path=db_path
            )
            remove_player(command)
            return {"status": "success", "message": f"Player '{parameters['name']}' removed"}
        
        elif tool_name == "backup":
            command = BackupCommand(
                backup_path=Path(parameters["backup_path"]),
                db_path=db_path
            )
            result = backup(command)
            return {"status": "success", "message": result}
        
        else:
            return {"error": f"Unknown tool: {tool_name}"}
    
    server.serve()