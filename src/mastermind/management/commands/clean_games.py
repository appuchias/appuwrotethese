# Appu Wrote These
# Copyright (C) 2023  Appuchia <appuchia@appu.ltd>

from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from mastermind import models


class Command(BaseCommand):
    help = "Removes all games without guesses."

    def handle(self, *args, **options):
        # Remove all games without guesses
        games = models.Game.objects.all()

        deleted = 0

        for game in games:
            # Prevent deleting games that are less than an hour old
            if game.created > datetime.now() - timedelta(hours=6):
                continue

            # Delete unfinished games
            if not game.is_finished():
                game.delete()
                deleted += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully deleted {deleted} games."))
