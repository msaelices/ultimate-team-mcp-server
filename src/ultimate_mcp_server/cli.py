import sys
from pathlib import Path
from datetime import date
import click

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
    SurfaceType
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

@cli.command("add-tournament")
@click.option("--name", "-n", required=True, help="Tournament name")
@click.option("--location", "-l", required=True, help="Tournament location")
@click.option("--date", "-d", required=True, type=click.DateTime(formats=["%Y-%m-%d"]), 
              help="Tournament date (YYYY-MM-DD)")
@click.option("--surface", "-s", type=click.Choice(["grass", "beach"]), required=True,
              help="Playing surface type (grass or beach)")
@click.option("--registration-deadline", "-r", required=True, 
              type=click.DateTime(formats=["%Y-%m-%d"]), 
              help="Registration deadline (YYYY-MM-DD)")
@click.option("--db-uri", default=DEFAULT_DB_URI, help="Database URI (sqlitecloud:// or file://)")
def add_tournament_command(name, location, date, surface, registration_deadline, db_uri):
    """Add a new tournament to the database."""
    try:
        command = AddTournamentCommand(
            name=name,
            location=location,
            date=date.date(),
            surface=SurfaceType(surface),
            registration_deadline=registration_deadline.date(),
            db_uri=db_uri
        )
        result = add_tournament(command)
        click.echo(f"Added tournament: {result.name} (ID: {result.id})")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@cli.command("list-tournaments")
@click.option("--limit", "-l", default=1000, help="Maximum number of tournaments to list")
@click.option("--db-uri", default=DEFAULT_DB_URI, help="Database URI (sqlitecloud:// or file://)")
def list_tournaments_command(limit, db_uri):
    """List tournaments in the database."""
    try:
        command = ListTournamentsCommand(
            limit=limit,
            db_uri=db_uri
        )
        tournaments = list_tournaments(command)
        
        if not tournaments:
            click.echo("No tournaments found")
            return
        
        # Print the tournaments
        click.echo("Tournaments:")
        for tournament in tournaments:
            click.echo(f"- ID: {tournament.id}, Name: {tournament.name}")
            click.echo(f"  Location: {tournament.location}")
            click.echo(f"  Date: {tournament.date}")
            click.echo(f"  Surface: {tournament.surface.value}")
            click.echo(f"  Registration Deadline: {tournament.registration_deadline}")
            click.echo("")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@cli.command("update-tournament")
@click.option("--id", "-i", required=True, type=int, help="Tournament ID")
@click.option("--name", "-n", help="Tournament name")
@click.option("--location", "-l", help="Tournament location")
@click.option("--date", "-d", type=click.DateTime(formats=["%Y-%m-%d"]), 
              help="Tournament date (YYYY-MM-DD)")
@click.option("--surface", "-s", type=click.Choice(["grass", "beach"]),
              help="Playing surface type (grass or beach)")
@click.option("--registration-deadline", "-r", 
              type=click.DateTime(formats=["%Y-%m-%d"]), 
              help="Registration deadline (YYYY-MM-DD)")
@click.option("--db-uri", default=DEFAULT_DB_URI, help="Database URI (sqlitecloud:// or file://)")
def update_tournament_command(id, name, location, date, surface, registration_deadline, db_uri):
    """Update an existing tournament."""
    try:
        command = UpdateTournamentCommand(
            id=id,
            name=name,
            location=location,
            date=date.date() if date else None,
            surface=SurfaceType(surface) if surface else None,
            registration_deadline=registration_deadline.date() if registration_deadline else None,
            db_uri=db_uri
        )
        
        # Check if any fields were provided to update
        if all(v is None for v in [name, location, date, surface, registration_deadline]):
            click.echo("Error: At least one field must be specified to update.", err=True)
            sys.exit(1)
            
        result = update_tournament(command)
        click.echo(f"Updated tournament: {result.name} (ID: {result.id})")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@cli.command("remove-tournament")
@click.option("--id", "-i", required=True, type=int, help="ID of the tournament to remove")
@click.option("--db-uri", default=DEFAULT_DB_URI, help="Database URI (sqlitecloud:// or file://)")
def remove_tournament_command(id, db_uri):
    """Remove a tournament from the database."""
    try:
        command = RemoveTournamentCommand(
            id=id,
            db_uri=db_uri
        )
        result = remove_tournament(command)
        click.echo(result)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

if __name__ == "__main__":
    cli()