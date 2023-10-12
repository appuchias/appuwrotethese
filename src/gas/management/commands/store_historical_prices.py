from django.core.management.base import BaseCommand
from gas import db_actions


class Command(BaseCommand):
    help = "Add all historical prices to the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "-f",
            "--local-folder",
            type=str,
            help="Local folder to retrieve historical prices from.",
            default="",
        )
        parser.add_argument(
            "-d",
            "--days",
            type=int,
            help="Days to fetch",
            default=365,
        )

    def handle(self, *args, **options):
        db_actions.store_historical_prices(
            days=options["days"], local_folder=options["local_folder"]
        )
