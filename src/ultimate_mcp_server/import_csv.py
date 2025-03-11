import csv
from pathlib import Path

import click

from .modules.data_types import AddPlayerCommand
from .modules.functionality.add_player import add_player
from .modules.constants import DEFAULT_SQLITE_DATABASE_PATH


@click.command()
@click.argument("csv_file", type=click.Path(exists=True))
@click.option("--db", default=str(DEFAULT_SQLITE_DATABASE_PATH), help="Database path")
def import_csv(csv_file, db):
    """Import players from a CSV file."""
    db_path = Path(db)
    csv_path = Path(csv_file)

    with open(csv_path, "r", newline="") as file:
        reader = csv.DictReader(file)

        success_count = 0
        failure_count = 0

        for row in reader:
            try:
                # Normalize column names
                name = (
                    row.get("Nombre")
                    or row.get("Name")
                    or row.get("name")
                    or row.get("nombre")
                )
                phone = (
                    row.get("Telefono")
                    or row.get("Phone")
                    or row.get("phone")
                    or row.get("telefono")
                )
                email = row.get("Email") or row.get("email")

                if not name or not phone:
                    click.echo(f"Skipping row with missing data: {row}")
                    failure_count += 1
                    continue

                command = AddPlayerCommand(
                    name=name,
                    phone=phone,
                    email=email if email else None,
                )

                add_player(command)
                click.echo(f"Added player: {name}")
                success_count += 1

            except Exception as e:
                click.echo(f"Error adding player from row {row}: {str(e)}")
                failure_count += 1

        click.echo(
            f"Import complete. {success_count} players added, {failure_count} failures."
        )


if __name__ == "__main__":
    import_csv()

