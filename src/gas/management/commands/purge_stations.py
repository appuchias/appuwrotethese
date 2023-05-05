from django.core.management.base import BaseCommand
from gas import db_actions


class Command(BaseCommand):
    help = "Removes all gas stations from the database."

    def handle(self, *args, **options):
        db_actions.purge_stations()
