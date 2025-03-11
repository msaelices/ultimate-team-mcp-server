import sys
from pathlib import Path
import click

from .modules.data_types import (
    AddPlayerCommand,
    ListPlayersCommand,
    RemovePlayerCommand,
    BackupCommand,
    ImportPlayersCommand
)
from .modules.functionality.add_player import add_player
from .modules.functionality.list_players import list_players
from .modules.functionality.remove_player import remove_player
from .modules.functionality.backup import backup
from .modules.functionality.import_players import import_players
from .modules.constants import DEFAULT_DB_URI

@click.group()
def cli():
    """FDU - Ultimate Frisbee Team Management"""
    pass

@cli.command("add-player")
@click.argument("name")
@click.option("--phone", "-p", required=True, help="Player's phone number")
@click.option("--email", "-e", help="Player's email address")
@click.option("--db-uri", default=DEFAULT_DB_URI, help="Database URI (sqlitecloud:// or file://)")
def add_player_command(name, phone, email, db_uri):
    """Add a new player to the database."""
    try:
        command = AddPlayerCommand(
            name=name,
            phone=phone,
            email=email,
            db_uri=db_uri
        )
        player = add_player(command)
        click.echo(f"Added player: {player.name}")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@cli.command("list-players")
@click.option("--limit", "-l", default=1000, help="Maximum number of players to list")
@click.option("--db-uri", default=DEFAULT_DB_URI, help="Database URI (sqlitecloud:// or file://)")
def list_players_command(limit, db_uri):
    """List players in the database."""
    try:
        command = ListPlayersCommand(
            limit=limit,
            db_uri=db_uri
        )
        players = list_players(command)
        
        if not players:
            click.echo("No players found")
            return
        
        # Print the players
        click.echo("Players:")
        for player in players:
            email_display = f", Email: {player.email}" if player.email else ""
            click.echo(f"- {player.name} (Phone: {player.phone}{email_display})")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@cli.command("remove-player")
@click.option("--name", "-n", required=True, help="Name of the player to remove")
@click.option("--db-uri", default=DEFAULT_DB_URI, help="Database URI (sqlitecloud:// or file://)")
def remove_player_command(name, db_uri):
    """Remove a player from the database."""
    try:
        command = RemovePlayerCommand(
            name=name,
            db_uri=db_uri
        )
        remove_player(command)
        click.echo(f"Player '{name}' removed successfully")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@cli.command("backup")
@click.argument("backup_path")
@click.option("--db-uri", default=DEFAULT_DB_URI, help="Database URI (sqlitecloud:// or file://)")
def backup_command(backup_path, db_uri):
    """Backup the database to a file."""
    try:
        command = BackupCommand(
            backup_path=Path(backup_path),
            db_uri=db_uri
        )
        result = backup(command)
        click.echo(result)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@cli.command("import-players")
@click.argument("csv_file", type=click.Path(exists=True))
@click.option("--db-uri", default=DEFAULT_DB_URI, help="Database URI (sqlitecloud:// or file://)")
def import_players_command(csv_file, db_uri):
    """Import players from a CSV file, updating existing players.
    
    CSV_FILE must be a CSV file with headers. The following headers are recognized:
    - name/nombre: The player's name (required)
    - phone/telefono: The player's phone number (required)
    - email: The player's email address (optional)
    """
    try:
        command = ImportPlayersCommand(
            csv_path=Path(csv_file),
            db_uri=db_uri
        )
        
        players, errors = import_players(command)
        
        # Print results
        if players:
            click.echo(f"Successfully imported/updated {len(players)} players:")
            for player in players:
                email_display = f", Email: {player.email}" if player.email else ""
                click.echo(f"- {player.name} (Phone: {player.phone}{email_display})")
        
        if errors:
            click.echo(f"\nEncountered {len(errors)} errors:")
            for error in errors:
                click.echo(f"- {error}")
                
        click.echo(f"\nImport complete: {len(players)} successes, {len(errors)} failures.")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

if __name__ == "__main__":
    cli()