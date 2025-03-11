# FDU - Ultimate Frisbee Team MCP Server

For a Ultimate Frisbee team, we need a way to manage our players and their contact information. We also need a way to backup this information in case of a catastrophic failure. We also need a way to remove players from the team.

To implement this we'll...
1. Build the key sqlite functionality
2. Test the functionality with pytest
3. Expose the functionality via MCP server.

## SQLITE Database Structure

```
CREATE TABLE if not exists PLAYERS {
    name: str,
    created: datetime,
    phone: str,
    email: str,
}
```

## Implementation Notes
- DEFAULT_SQLITE_DATABASE_PATH = Path.home() / ".fdu.db" - place in constants.py
- mcp comands will return whatever the command returns.
- mirror ai_docs/pocket-pick-repomix-output.xml structure to understand how to setup the mcp server
- libraries should be
  - click
  - mcp
  - pydantic
  - pytest (dev dependency)
  - sqlite3 (standard library)
- use `uv add <package>` to add libraries.
- we're using uv to manage the project.
- add ultimate-team-mcp-server = "fdu_mcp_server:main" to the project.scripts section in pyproject.toml

## API

```
fdu add-player <name> \
    --phone, p: str
    --email, e: str (optional)
    --db: str = DEFAULT_SQLITE_DATABASE_PATH

fdu list-players \
    --limit, -l: number = 1000 \
    --db: str = DEFAULT_SQLITE_DATABASE_PATH

fdu remove-player \
    --name, -n: str \
    --db: str = DEFAULT_SQLITE_DATABASE_PATH

fdu backup <backup_absolute_path> \
    --db: str = DEFAULT_SQLITE_DATABASE_PATH

fdu import-players <csv_file_path> \
    --db: str = DEFAULT_SQLITE_DATABASE_PATH
```

### Example API Calls (for find modes)
```
# basic sqlite substring search
fdu add-player "John Smith" --phone +3455555555 --email john.smith@example.com

# list players
fdu list-players

# remove player
fdu remove-player --name "John Smith"

# import players from CSV file (updates existing ones)
fdu import-players /path/to/players.csv

```

## Project Structure
- src/
  - mcp_server_pocket_pick/
    - __init__.py - MIRROR ai_docs/mcp-server-git-repomix-output.xml
    - __main__.py - MIRROR ai_docs/mcp-server-git-repomix-output.xml
    - server.py - MIRROR but use our functionality
      - serve(sqlite_database: Path | None) -> None
      - pass sqlite_database to every tool call (--db arg)
    - modules/
      - __init__.py
      - init_db.py
      - data_types.py
        - class AddCommand(BaseModel) {text: str, tags: list[str] = [], db_path: Path = DEFAULT_SQLITE_DATABASE_PATH}
        - ...
      - constants.py
        - DEFAULT_SQLITE_DATABASE_PATH: Path = Path.home() / ".pocket_pick.db"
      - functionality/
        - add_player.py
        - list_players.py
        - remove_player.py
        - backup.py
    - tests/
      - __init__.py
      - test_init_db.py
      - functionality/
        - test_add_player.py
        - test_list_players.py
        - test_remove_player.py
        - test_backup.py
    

## Validation (close the loop)
- use `uv run pytest` to validate the tests pass.
- use `uv run ultimate-team-mcp-server --help` to validate the mcp server works.
