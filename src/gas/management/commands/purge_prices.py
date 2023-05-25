from django.core.management.base import BaseCommand
from gas import models


class Command(BaseCommand):
    help = "Removes all prices from the database."

    def handle(self, *args, **options):
        models.StationPrice.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Prices purged."))
