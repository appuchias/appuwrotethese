from datetime import date
from django.core.management.base import BaseCommand

from gas import db_actions


class Command(BaseCommand):
    help = "Updates the database for the gas app"

    def add_arguments(self, parser):
        parser.add_argument(
            "--update",
            action="store_true",
            help="Whether to update existing stations and prices",
            default=False,
        )

    def handle(self, *args, **options):
        db_actions.create_localities_provinces()
        db_actions.update_day_stations_prices(
            db_actions.get_data()["ListaEESSPrecio"], date.today(), options["update"]
        )

        self.stdout.write(self.style.SUCCESS("Successfully updated the database."))
