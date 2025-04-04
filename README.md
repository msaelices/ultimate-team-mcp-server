# Ultimate Frisbee Team MCP Server

A Model Context Protocol (MCP) server for managing Ultimate Frisbee Team players, tournaments, etc. This server allows you to add, list, and remove players from a SQLite database, as well as backup the database. Now uses FastMCP for improved performance and usability!

## Features

- Add players with their name, phone number, and optional email
- List all players in the database
- Remove players from the database
- Backup the database to a file
- Import players from a CSV file
- Accessible via CLI or MCP interface
- Now using FastMCP for improved AI interaction!

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

4. Set up environment variables (optional, for SQLiteCloud):
   
   Copy the .env-template file to .env and fill in the appropriate values:
   ```bash
   cp .env-template .env
   # Edit .env with your SQLiteCloud credentials
   ```

5. Run tests:
```bash
pytest tests/
```

## Usage

### CLI Usage

```bash
# Add a player
ultimate-team-mcp-server add-player "John Smith" --phone "+1234567890" --email "john@example.com"

# List all players
ultimate-team-mcp-server list-players

# Remove a player
ultimate-team-mcp-server remove-player --name "John Smith"

# Backup the database
ultimate-team-mcp-server backup /path/to/backup.db

# Import players from a CSV file, updating existing ones
ultimate-team-mcp-server import-players /path/to/players.csv

# Using with a specific database URI
ultimate-team-mcp-server list-players --db-uri "sqlitecloud://host:port/database?apikey=key"
ultimate-team-mcp-server add-player "John" --phone "+1234567890" --db-uri "file:///path/to/custom.db"
```

### MCP Server Usage

1. Start the MCP server:
```bash
ultimate-team-mcp-server
```

2. Install Claude Code.

3. Add the Ultimate Team MCP server directly to Claude:

```bash
# Set up with the new FastMCP-based server
# This works with both Claude Desktop and Claude CLI
claude mcp add ultimate -- ultimate-team-mcp-server

# List existing MCP servers - Validate that the server is running
claude mcp list
```

4. Use the server via Claude's web interface or CLI.

#### Using with custom database URI

You can specify a database URI when starting the server:

```bash
# Using environment variable
SQLITE_URI="sqlitecloud://host:port/database?apikey=key" ultimate-team-mcp-server

# Or using command-line option
ultimate-team-mcp-server --db-uri "sqlitecloud://host:port/database?apikey=key"
```

## Database Structure

The server can use either local SQLite or SQLiteCloud to store player information. The database schema is:

```sql
CREATE TABLE players (
    name TEXT PRIMARY KEY,
    created TIMESTAMP,
    phone TEXT,
    email TEXT
)
```

### Database Configuration

The server can connect to either a local SQLite database or SQLiteCloud for a cloud-based solution using a single database URI parameter. To configure the database connection:

1. Create a `.env` file based on the provided `.env-template`
2. Set the `SQLITE_URI` or `DB_URI` environment variable to one of the following formats:
   - For SQLiteCloud: `SQLITE_URI=sqlitecloud://hostname:port/database?apikey=your_api_key`
   - For local SQLite: `SQLITE_URI=file:///path/to/database.db`

If neither environment variable is set, the server will default to using a local SQLite database at `~/.ultimate.db`.

## CSV Import Format

The CSV import features (both import-csv and import-players) accept files with the following format:

```csv
Nombre,Telefono,Email
John Smith,+1234567890,john@example.com
Jane Doe,+0987654321,jane@example.com
```

Column names are case-insensitive and can be in English or Spanish (Nombre/Name, Telefono/Phone, Email).

### Difference between import-csv and import-players

- **import-csv**: The original import tool. It adds new players but fails if a player with the same name already exists.
- **import-players**: The enhanced import tool. It adds new players AND updates existing ones if a player with the same name is found.

Example of updating a player with import-players:

1. If your database has a player "John Smith" with phone "+1234567890"
2. And your CSV has "John Smith" with phone "+9999999999"
3. After import-players, "John Smith" will have the updated phone number "+9999999999"