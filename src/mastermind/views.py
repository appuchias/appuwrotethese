# Appu Wrote These
# Copyright (C) 2023  Appuchia <appuchia@appu.ltd>

import uuid

from django.contrib import messages
from django.http import HttpRequest, HttpResponseNotAllowed
from django.shortcuts import render, redirect
from django.utils.translation import gettext_lazy as _

from mastermind.models import Game, Guess
from mastermind.forms import MastermindGuess

validate_guess = lambda guess: (
    len(set(guess)) == 4 and all(digit in "0123456789" for digit in guess)
)


def home(request: HttpRequest):
    return render(request, "mastermind/home.html")


def play(request: HttpRequest, game_id: uuid.UUID | None = None):
    if not game_id:
        game_obj = Game()
        game_obj.save()

        game_id = Game.objects.latest("game_id").game_id

        return redirect("play", game_id=game_id)

    try:
        game_obj = Game.objects.get(game_id=str(game_id).zfill(4))
    except Game.DoesNotExist:
        messages.error(request, "Game does not exist.")
        return redirect("mastermind-home")

    if game_obj.is_finished():
        messages.error(request, "Game is finished.")
        return redirect("game", game_id=game_id)

    guesses = list(Guess.objects.filter(game=game_obj).order_by("created"))
    return render(
        request,
        "mastermind/play.html",
        {"game": game_obj, "guesses": guesses, "form": MastermindGuess()},
    )


def guess(request: HttpRequest, game_id: uuid.UUID):
    allowed_methods = ["POST"]
    if request.method not in allowed_methods:
        return HttpResponseNotAllowed(allowed_methods)

    form = MastermindGuess(request.POST)
    if not form.is_valid():
        messages.error(request, "Invalid form.")
        return redirect("mastermind-home")

    guess = str(form.cleaned_data["guess"]).zfill(4)

    game_obj = Game.objects.get(game_id=game_id)
    guess_count = game_obj.get_guess_count()

    if guess_count >= 10:
        messages.error(request, _("You have already made 10 guesses") + ".")
        return redirect("game", game_id=game_id)

    if not validate_guess(guess):
        messages.error(request, _("Invalid guess") + ".")
        return redirect("play", game_id=game_id)

    correct, misplaced = game_obj.check_guess(game_obj.code, guess)

    guess_obj = Guess(game=game_obj, guess=guess, correct=correct, misplaced=misplaced)
    guess_obj.save()

    if correct == 4:
        game_obj.won = True
        game_obj.save()
        messages.success(request, "You won!")
        return redirect("game", game_id=game_id)

    if guess_count == 9:
        game_obj.lost = True
        game_obj.save()
        messages.error(request, "You lost!")
        return redirect("game", game_id=game_id)

    return redirect("play", game_id=game_id)


def game(request: HttpRequest, game_id: int):
    try:
        game_obj = Game.objects.get(game_id=str(game_id).zfill(4))
    except Game.DoesNotExist:
        messages.error(request, "Game does not exist.")
        return redirect("mastermind-home")

    if not game_obj.is_finished():
        messages.error(request, "Game is not finished.")
        return redirect("mastermind-home")

    guesses = list(Guess.objects.filter(game=game_obj).order_by("created"))
    return render(
        request,
        "mastermind/game.html",
        {"game": game_obj, "guesses": guesses},
    )
