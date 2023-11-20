# Appu Wrote These
# Copyright (C) 2023  Appuchia <appuchia@appu.ltd>

from django.core.management.base import BaseCommand

from mastermind import models


class Command(BaseCommand):
    help = "Removes all games without guesses."

    def handle(self, *args, **options):
        # Remove all games without guesses
        games = models.Game.objects.all()

        for game in games:
            if game.guesses.count() == 0:  # type: ignore
                game.delete()
