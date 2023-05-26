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

    def handle(self, *args, **options):
        if options["local_folder"]:
            db_actions.store_historical_prices(options["local_folder"])  # type: ignore
        else:
            db_actions.store_historical_prices()
