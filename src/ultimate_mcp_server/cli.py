import sys
from pathlib import Path
from datetime import date, datetime
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
    RegisterPlayerCommand,
    UnregisterPlayerCommand,
    ListTournamentPlayersCommand,
    ListPlayerTournamentsCommand,
    MarkPaymentCommand,
    ClearPaymentCommand,
    AddFederationPaymentCommand,
    RemoveLastFederationPaymentCommand,
    ListFederationPaymentsCommand,
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
from .modules.functionality.register_player import register_player
from .modules.functionality.unregister_player import unregister_player
from .modules.functionality.list_tournament_players import list_tournament_players, PlayerWithPayment
from .modules.functionality.list_player_tournaments import list_player_tournaments
from .modules.functionality.mark_payment import mark_payment
from .modules.functionality.clear_payment import clear_payment
from .modules.functionality.add_federation_payment import add_federation_payment
from .modules.functionality.remove_last_federation_payment import remove_last_federation_payment
from .modules.functionality.list_federation_payments import list_federation_payments
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

@cli.command("register-player")
@click.option("--tournament-id", "-t", required=True, type=int, help="Tournament ID")
@click.option("--player-name", "-p", required=True, help="Name of the player to register")
@click.option("--db-uri", default=DEFAULT_DB_URI, help="Database URI (sqlitecloud:// or file://)")
def register_player_command(tournament_id, player_name, db_uri):
    """Register a player for a tournament."""
    try:
        command = RegisterPlayerCommand(
            tournament_id=tournament_id,
            player_name=player_name,
            db_uri=db_uri
        )
        result = register_player(command)
        click.echo(f"Player '{result.player_name}' registered for tournament ID {result.tournament_id}")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command("unregister-player")
@click.option("--tournament-id", "-t", required=True, type=int, help="Tournament ID")
@click.option("--player-name", "-p", required=True, help="Name of the player to unregister")
@click.option("--db-uri", default=DEFAULT_DB_URI, help="Database URI (sqlitecloud:// or file://)")
def unregister_player_command(tournament_id, player_name, db_uri):
    """Unregister a player from a tournament."""
    try:
        command = UnregisterPlayerCommand(
            tournament_id=tournament_id,
            player_name=player_name,
            db_uri=db_uri
        )
        result = unregister_player(command)
        click.echo(result)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command("list-tournament-players")
@click.option("--tournament-id", "-t", required=True, type=int, help="Tournament ID")
@click.option("--limit", "-l", default=1000, help="Maximum number of players to list")
@click.option("--db-uri", default=DEFAULT_DB_URI, help="Database URI (sqlitecloud:// or file://)")
def list_tournament_players_command(tournament_id, limit, db_uri):
    """List all players registered for a tournament."""
    try:
        command = ListTournamentPlayersCommand(
            tournament_id=tournament_id,
            limit=limit,
            db_uri=db_uri
        )
        tournament, players = list_tournament_players(command)
        
        # Print tournament details
        click.echo(f"Tournament: {tournament.name} (ID: {tournament.id})")
        click.echo(f"Location: {tournament.location}")
        click.echo(f"Date: {tournament.date}")
        click.echo(f"Surface: {tournament.surface.value}")
        
        if not players:
            click.echo("\nNo players registered for this tournament")
            return
        
        # Print registered players with payment info
        click.echo(f"\nRegistered Players ({len(players)}):")
        for player_info in players:
            player = player_info.player
            email_display = f", Email: {player.email}" if player.email else ""
            payment_status = "[PAID]" if player_info.has_paid else "[UNPAID]"
            payment_date = f" on {player_info.payment_date.strftime('%Y-%m-%d')}" if player_info.payment_date else ""
            
            click.echo(f"- {player.name} {payment_status}{payment_date}")
            click.echo(f"  Phone: {player.phone}{email_display}")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command("list-player-tournaments")
@click.option("--player-name", "-p", required=True, help="Name of the player")
@click.option("--limit", "-l", default=1000, help="Maximum number of tournaments to list")
@click.option("--db-uri", default=DEFAULT_DB_URI, help="Database URI (sqlitecloud:// or file://)")
def list_player_tournaments_command(player_name, limit, db_uri):
    """List all tournaments a player is registered for."""
    try:
        command = ListPlayerTournamentsCommand(
            player_name=player_name,
            limit=limit,
            db_uri=db_uri
        )
        player, tournaments = list_player_tournaments(command)
        
        # Print player details
        click.echo(f"Player: {player.name}")
        click.echo(f"Phone: {player.phone}")
        if player.email:
            click.echo(f"Email: {player.email}")
        
        if not tournaments:
            click.echo("\nPlayer is not registered for any tournaments")
            return
        
        # Print registered tournaments
        click.echo(f"\nRegistered Tournaments ({len(tournaments)}):")
        for tournament in tournaments:
            click.echo(f"- ID: {tournament.id}, Name: {tournament.name}")
            click.echo(f"  Date: {tournament.date}, Location: {tournament.location}")
            click.echo(f"  Surface: {tournament.surface.value}")
            click.echo("")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command("mark-payment")
@click.option("--tournament-id", "-t", required=True, type=int, help="Tournament ID")
@click.option("--player-name", "-p", required=True, help="Name of the player")
@click.option("--payment-date", "-d", type=click.DateTime(formats=["%Y-%m-%d"]), 
              help="Payment date (YYYY-MM-DD), defaults to today")
@click.option("--db-uri", default=DEFAULT_DB_URI, help="Database URI (sqlitecloud:// or file://)")
def mark_payment_command(tournament_id, player_name, payment_date, db_uri):
    """Mark a player as having paid for a tournament."""
    try:
        # Convert date to datetime if provided
        payment_datetime = payment_date.replace(hour=12) if payment_date else None
        
        command = MarkPaymentCommand(
            tournament_id=tournament_id,
            player_name=player_name,
            payment_date=payment_datetime,
            db_uri=db_uri
        )
        result = mark_payment(command)
        
        payment_date_str = result.payment_date.strftime("%Y-%m-%d %H:%M")
        click.echo(f"Player '{result.player_name}' marked as paid for tournament ID {result.tournament_id}")
        click.echo(f"Payment date: {payment_date_str}")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command("clear-payment")
@click.option("--tournament-id", "-t", required=True, type=int, help="Tournament ID")
@click.option("--player-name", "-p", required=True, help="Name of the player")
@click.option("--db-uri", default=DEFAULT_DB_URI, help="Database URI (sqlitecloud:// or file://)")
def clear_payment_command(tournament_id, player_name, db_uri):
    """Clear a player's payment status for a tournament."""
    try:
        command = ClearPaymentCommand(
            tournament_id=tournament_id,
            player_name=player_name,
            db_uri=db_uri
        )
        result = clear_payment(command)
        click.echo(f"Payment status cleared for player '{result.player_name}' in tournament ID {result.tournament_id}")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command("add-federation-payment")
@click.option("--player-name", "-p", required=True, help="Name of the player")
@click.option("--amount", "-a", required=True, type=float, help="Payment amount")
@click.option("--payment-date", "-d", type=click.DateTime(formats=["%Y-%m-%d"]), 
              default=lambda: datetime.now().date(), help="Payment date (YYYY-MM-DD), defaults to today")
@click.option("--notes", "-n", help="Optional notes about the payment")
@click.option("--db-uri", default=DEFAULT_DB_URI, help="Database URI (sqlitecloud:// or file://)")
def add_federation_payment_command(player_name, amount, payment_date, notes, db_uri):
    """Add a federation payment for a player."""
    try:
        # Convert date to datetime with noon time to avoid timezone issues
        payment_datetime = datetime.combine(payment_date.date(), datetime.min.time().replace(hour=12))
        
        command = AddFederationPaymentCommand(
            player_name=player_name,
            payment_date=payment_datetime,
            amount=amount,
            notes=notes,
            db_uri=db_uri
        )
        
        result = add_federation_payment(command)
        
        click.echo(f"Federation payment added for player '{result.player_name}'")
        click.echo(f"Payment ID: {result.id}")
        click.echo(f"Amount: {result.amount}")
        click.echo(f"Date: {result.payment_date.strftime('%Y-%m-%d')}")
        if result.notes:
            click.echo(f"Notes: {result.notes}")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command("remove-last-federation-payment")
@click.option("--player-name", "-p", required=True, help="Name of the player")
@click.option("--db-uri", default=DEFAULT_DB_URI, help="Database URI (sqlitecloud:// or file://)")
def remove_last_federation_payment_command(player_name, db_uri):
    """Remove the most recent federation payment for a player."""
    try:
        command = RemoveLastFederationPaymentCommand(
            player_name=player_name,
            db_uri=db_uri
        )
        
        result = remove_last_federation_payment(command)
        
        if result:
            click.echo(f"Removed federation payment for player '{result.player_name}'")
            click.echo(f"Payment ID: {result.id}")
            click.echo(f"Amount: {result.amount}")
            click.echo(f"Date: {result.payment_date.strftime('%Y-%m-%d')}")
            if result.notes:
                click.echo(f"Notes: {result.notes}")
        else:
            click.echo(f"No federation payments found for player '{player_name}'")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command("list-federation-payments")
@click.option("--player-name", "-p", required=True, help="Name of the player")
@click.option("--limit", "-l", default=100, help="Maximum number of payments to list")
@click.option("--db-uri", default=DEFAULT_DB_URI, help="Database URI (sqlitecloud:// or file://)")
def list_federation_payments_command(player_name, limit, db_uri):
    """List all federation payments for a player."""
    try:
        command = ListFederationPaymentsCommand(
            player_name=player_name,
            limit=limit,
            db_uri=db_uri
        )
        
        player, payments = list_federation_payments(command)
        
        # Print player details
        click.echo(f"Player: {player.name}")
        click.echo(f"Phone: {player.phone}")
        if player.email:
            click.echo(f"Email: {player.email}")
        
        if not payments:
            click.echo("\nNo federation payments found for this player")
            return
        
        # Print federation payments
        click.echo(f"\nFederation Payments ({len(payments)}):")
        
        # Calculate total
        total_amount = sum(payment.amount for payment in payments)
        
        for payment in payments:
            click.echo(f"- ID: {payment.id}, Date: {payment.payment_date.strftime('%Y-%m-%d')}")
            click.echo(f"  Amount: {payment.amount:.2f}")
            if payment.notes:
                click.echo(f"  Notes: {payment.notes}")
        
        click.echo(f"\nTotal Payments: {total_amount:.2f}")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()