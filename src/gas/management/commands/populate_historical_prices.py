from django.core.management.base import BaseCommand
from gas import db_actions


class Command(BaseCommand):
    help = "Add all historical prices to the database."

    def handle(self, *args, **options):
        db_actions.store_historical_prices()
