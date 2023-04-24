from django.core.management.base import BaseCommand
from gas import db_updater


class Command(BaseCommand):
    help = "Updates the database for the gas app"

    def handle(self, *args, **options):
        db_updater.update_db()
