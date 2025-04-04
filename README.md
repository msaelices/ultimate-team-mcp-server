# Ultimate Frisbee Team MCP Server

A Model Context Protocol (MCP) server for managing Ultimate Frisbee Team players, tournaments, and payments. This server allows you to add, list, and manage players and tournaments in a SQLite database, as well as track tournament registrations and payments. Now uses FastMCP for improved performance and usability!

## Features

### Player Management
- Add players with their name, phone number, and optional email
- List all players in the database
- Remove players from the database
- Import players from a CSV file

### Tournament Management
- Create tournaments with name, location, date, surface type (grass/beach), and registration deadline
- List, update, and remove tournaments
- Register/unregister players for tournaments
- Track tournament payment status for each player
- Search for players who have paid for a tournament with fuzzy name matching

### Federation Payment Tracking
- Record federation payments made by players
- Track payment amounts and dates
- List payment history for players
- Remove the most recent payment if needed

### System Features
- Backup the database to a file
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

#### Player Management

```bash
# Add a player
ultimate-team-mcp-server add-player "John Smith" --phone "+1234567890" --email "john@example.com"

# List all players
ultimate-team-mcp-server list-players

# Remove a player
ultimate-team-mcp-server remove-player --name "John Smith"

# Import players from a CSV file, updating existing ones
ultimate-team-mcp-server import-players /path/to/players.csv
```

#### Tournament Management

```bash
# Add a tournament
ultimate-team-mcp-server add-tournament --name "Summer Championship" --location "City Beach" \
  --date "2025-07-15" --surface "beach" --registration-deadline "2025-06-30"

# List all tournaments
ultimate-team-mcp-server list-tournaments

# Update a tournament
ultimate-team-mcp-server update-tournament --id 1 --name "Summer Beach Championship" --location "North Beach"

# Remove a tournament
ultimate-team-mcp-server remove-tournament --id 1

# Register a player for a tournament
ultimate-team-mcp-server register-player --tournament-id 1 --player-name "John Smith"

# Unregister a player from a tournament
ultimate-team-mcp-server unregister-player --tournament-id 1 --player-name "John Smith"

# List all players registered for a tournament
ultimate-team-mcp-server list-tournament-players --tournament-id 1

# List all tournaments a player is registered for
ultimate-team-mcp-server list-player-tournaments --player-name "John Smith"

# Mark a player as having paid for a tournament
ultimate-team-mcp-server mark-payment --tournament-id 1 --player-name "John Smith"

# Clear a player's payment status for a tournament
ultimate-team-mcp-server clear-payment --tournament-id 1 --player-name "John Smith"

# Search for players who have paid for a tournament (with fuzzy matching)
ultimate-team-mcp-server search-paid-players --tournament-id 1 --name "John"
```

#### Federation Payment Tracking

```bash
# Add a federation payment for a player
ultimate-team-mcp-server add-federation-payment --player-name "John Smith" \
  --amount 50.0 --payment-date "2025-01-15" --notes "Annual fee"

# List all federation payments for a player
ultimate-team-mcp-server list-federation-payments --player-name "John Smith"

# Remove the most recent federation payment for a player
ultimate-team-mcp-server remove-last-federation-payment --player-name "John Smith"
```

#### System Commands

```bash
# Backup the database
ultimate-team-mcp-server backup /path/to/backup.db

# Using with a specific database URI
ultimate-team-mcp-server list-players --db-uri "sqlitecloud://host:port/database?apikey=key"
ultimate-team-mcp-server add-player "John" --phone "+1234567890" --db-uri "file:///path/to/custom.db"
```


### Usage with Claude Desktop

To use the MCP server with Claude Desktop, you need to add it to your `claude_desktop_config.json` file:

```json
{
    "mcpServers": {
        "ultimate_mcp_server": {
            "command": "ultimate-team-mcp-server",
            "environment": {
            "SQLITE_URI": "sqlitecloud://host:port/database?apikey=key"
            }
        }
    }
}
```

### Usage with Claude Code


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

Run Claude code with the following command:

```bash
claude
```

#### Using with custom database URI

You can specify a database URI when starting the server:

```bash
# Using environment variable
SQLITE_URI="sqlitecloud://host:port/database?apikey=key" ultimate-team-mcp-server

# Or using command-line option
ultimate-team-mcp-server --db-uri "sqlitecloud://host:port/database?apikey=key"
```

## Database Structure

The server uses SQLite or SQLiteCloud to store player data, tournaments, registrations, payments, and related information. The database now includes tables for:

- Players (name, contact info)
- Tournaments (name, location, date, surface type, registration deadline)
- Tournament-Player registrations (with payment tracking)
- Federation payments (with amount and payment history)

The complete schema definition is located in the `src/ultimate_mcp_server/modules/init_db.py` file.

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
