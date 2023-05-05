from django.core.management.base import BaseCommand
from gas import db_actions


class Command(BaseCommand):
    help = "Updates the database for the gas app"

    def handle(self, *args, **options):
        db_actions.update_db()
