from django.core.management.base import BaseCommand
from gas import models


class Command(BaseCommand):
    help = "Removes all gas stations from the database."

    def handle(self, *args, **options):
        models.Station.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Stations purged."))
