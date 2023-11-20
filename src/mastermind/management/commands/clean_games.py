# Appu Wrote These
# Copyright (C) 2023  Appuchia <appuchia@appu.ltd>

from django.core.management.base import BaseCommand

from mastermind import models


class Command(BaseCommand):
    help = "Removes all games without guesses."

    def handle(self, *args, **options):
        # Remove all games without guesses
        games = models.Game.objects.all()

        deleted = 0

        for game in games:
            if game.guesses.count() == 0:  # type: ignore
                game.delete()
                deleted += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully deleted {deleted} games."))
