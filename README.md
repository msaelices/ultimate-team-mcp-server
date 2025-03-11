# FDU MCP Server

A Model Context Protocol (MCP) server for managing Ultimate Frisbee Team players. This server allows you to add, list, and remove players from a database, as well as backup the database.

## Features

- Add players with their name, phone number, and optional email
- List all players in the database
- Remove players from the database
- Backup the database to a file
- Import players from a CSV file
- Accessible via CLI or MCP interface

## Setup

### Environment Setup

1. Create a virtual environment with uv:
```bash
uv venv
```

2. Activate the virtual environment:
```bash
source .venv/bin/activate
```

3. Install the package in development mode with dev dependencies:
```bash
pip install -e ".[dev]"
```

   Or using uv:
   ```bash
   uv pip install -e ".[dev]"
   ```

4. Run tests:
```bash
pytest tests/
```

## Usage

### CLI Usage

```bash
# Add a player
fdu-mcp-server add-player "John Smith" --phone "+1234567890" --email "john@example.com"

# List all players
fdu-mcp-server list-players

# Remove a player
fdu-mcp-server remove-player --name "John Smith"

# Backup the database
fdu-mcp-server backup /path/to/backup.db

# Import players from a CSV file
fdu-mcp-server import-csv /path/to/players.csv
```

### MCP Server Usage

1. Start the MCP server:
```bash
fdu-mcp-server
```

2. Install Claude Code.

3. Add the FDU MCP server:
```bash
# Add the FDU MCP server
claude mcp add fdu -- fdu-mcp-server

# List existing MCP servers - Validate that the server is running
claude mcp list
```

4. Use the server via Claude:
```bash
claude
```

## Database Structure

The server uses SQLite to store player information. The database schema is:

```sql
CREATE TABLE players (
    name TEXT PRIMARY KEY,
    created TIMESTAMP,
    phone TEXT,
    email TEXT
)
```

## CSV Import Format

The CSV import feature accepts files with the following format:

```csv
Nombre,Telefono,Email
John Smith,+1234567890,john@example.com
Jane Doe,+0987654321,jane@example.com
```

Column names are case-insensitive and can be in English or Spanish.
