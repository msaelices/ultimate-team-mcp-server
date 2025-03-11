import sys
from pathlib import Path
import click

from .modules.data_types import (
    AddPlayerCommand,
    ListPlayersCommand,
    RemovePlayerCommand,
    BackupCommand
)
from .modules.functionality.add_player import add_player
from .modules.functionality.list_players import list_players
from .modules.functionality.remove_player import remove_player
from .modules.functionality.backup import backup
from .modules.constants import DEFAULT_SQLITE_DATABASE_PATH

@click.group()
def cli():
    """FDU - Ultimate Frisbee Team Management"""
    pass

@cli.command("add-player")
@click.argument("name")
@click.option("--phone", "-p", required=True, help="Player's phone number")
@click.option("--email", "-e", help="Player's email address")
@click.option("--db", default=str(DEFAULT_SQLITE_DATABASE_PATH), help="Database path")
def add_player_command(name, phone, email, db):
    """Add a new player to the database."""
    try:
        command = AddPlayerCommand(
            name=name,
            phone=phone,
            email=email,
            db_path=Path(db)
        )
        player = add_player(command)
        click.echo(f"Added player: {player.name}")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@cli.command("list-players")
@click.option("--limit", "-l", default=1000, help="Maximum number of players to list")
@click.option("--db", default=str(DEFAULT_SQLITE_DATABASE_PATH), help="Database path")
def list_players_command(limit, db):
    """List players in the database."""
    try:
        command = ListPlayersCommand(
            limit=limit,
            db_path=Path(db)
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
@click.option("--db", default=str(DEFAULT_SQLITE_DATABASE_PATH), help="Database path")
def remove_player_command(name, db):
    """Remove a player from the database."""
    try:
        command = RemovePlayerCommand(
            name=name,
            db_path=Path(db)
        )
        remove_player(command)
        click.echo(f"Player '{name}' removed successfully")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@cli.command("backup")
@click.argument("backup_path")
@click.option("--db", default=str(DEFAULT_SQLITE_DATABASE_PATH), help="Database path")
def backup_command(backup_path, db):
    """Backup the database to a file."""
    try:
        command = BackupCommand(
            backup_path=Path(backup_path),
            db_path=Path(db)
        )
        result = backup(command)
        click.echo(result)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

if __name__ == "__main__":
    cli()