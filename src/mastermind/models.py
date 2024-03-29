# Appu Wrote These
# Copyright (C) 2023  Appuchia <appuchia@appu.ltd>

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

from typing import Any
from random import shuffle
import uuid

DIGITS = "0123456789"


class Game(models.Model):
    game_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=4, null=False, blank=False)
    won = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.code = self.code or self._generate_code()

    def __str__(self):
        return f"{self.game_id}"

    def _generate_code(self) -> str:
        """Generate a random 4-digit code with no repeating digits."""

        code = list(DIGITS)
        shuffle(code)
        return "".join(code[:4])

    def check_guess(self, code: str, guess: str) -> tuple[int, int]:
        """Check the guess against the code and return the number of correct and misplaced digits."""

        correct = 0
        misplaced = 0
        for i, digit in enumerate(guess):
            if digit in code:
                if digit == code[i]:
                    correct += 1
                else:
                    misplaced += 1
        return correct, misplaced

    def is_finished(self) -> bool:
        return self.won or self.get_guess_count() >= 10

    def get_guess_count(self):
        return Guess.objects.filter(game=self).count()

    def get_last_guess(self):
        return Guess.objects.filter(game=self).order_by("-created").first()

    def get_all_guesses(self):
        return Guess.objects.filter(game=self).order_by("-created")

    def get_absolute_url(self):
        return reverse("game", kwargs={"id": self.game_id})

    class Meta:
        ordering = ["-created"]


class Guess(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="guesses")
    guess = models.CharField(max_length=4, null=False, blank=False)
    correct = models.IntegerField(null=False, blank=False)
    misplaced = models.IntegerField(null=False, blank=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.guess}"

    class Meta:
        ordering = ["-created"]
        verbose_name_plural = "Guesses"
