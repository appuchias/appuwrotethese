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
        add_upd_counts = db_actions.update_station_prices(
            {date.today(): db_actions.get_data()["ListaEESSPrecio"]}, options["update"]
        )
        add_stations, add_prices = add_upd_counts[0]
        upd_stations, upd_prices = add_upd_counts[1]

        self.stdout.write(self.style.SUCCESS("Successfully updated the database.\n"))
        self.stdout.write(
            self.style.SUCCESS(f"Add: {add_stations} stations, {add_prices} prices.")
        )
        self.stdout.write(
            self.style.SUCCESS(f"Update: {upd_stations} stations, {upd_prices} prices.")
        )
