# Appu Wrote These
# Copyright (C) 2023  Appuchia <appuchia@appu.ltd>

import uuid

from django.contrib import messages
from django.contrib.auth.models import User, AnonymousUser
from django.http import HttpRequest, HttpResponseNotAllowed
from django.shortcuts import render, redirect
from django.utils.translation import gettext_lazy as _
from appuwrotethese.settings import config


from mastermind.models import Game, Guess
from mastermind.forms import MastermindGuess


def _validate_guess(guess: str) -> bool:
    return len(set(guess)) == 4 and all(digit in "0123456789" for digit in guess)


def _get_mastermind_user() -> User:
    if uid := config.get("MASTERMIND_USER_ID", None):
        if not (user := User.objects.get(id=uid)):
            raise ValueError("MASTERMIND_USER_ID is invalid.")
        return user

    if not User.objects.filter(username="mastermind").exists():
        raise ValueError(
            "MASTERMIND_USER_ID not set and mastermind user does not exist."
        )

    return User.objects.get(username="mastermind")


def mastermind(request: HttpRequest):
    return render(request, "mastermind/home.html")


def play(request: HttpRequest, game_id: uuid.UUID | None = None):
    if not request.user.is_authenticated:
        request.user = _get_mastermind_user()

    if not game_id:
        game_obj = Game(user=request.user)
        game_obj.save()

        game_id = game_obj.game_id

        return redirect("play", game_id=game_id)

    try:
        game_obj = Game.objects.get(game_id=str(game_id).zfill(4))
    except Game.DoesNotExist:
        messages.error(request, _("Game does not exist") + ".")
        return redirect("mastermind")

    if game_obj.is_finished():
        messages.error(request, _("Game is finished") + ".")
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

    if not request.user.is_authenticated:
        request.user = _get_mastermind_user()

    form = MastermindGuess(request.POST)
    if not form.is_valid():
        messages.error(request, "Invalid form.")
        return redirect("mastermind")

    guess = str(form.cleaned_data["guess"]).zfill(4)

    game_obj = Game.objects.get(game_id=game_id)
    guess_count = game_obj.get_guess_count()

    if not game_obj.user == request.user:
        messages.error(request, "You are not the owner of this game.")
        return redirect("mastermind")

    if game_obj.is_finished():  # 10 guesses or more / won
        messages.error(request, _("You have already made 10 guesses") + ".")
        return redirect("game", game_id=game_id)

    if not _validate_guess(guess):
        messages.error(request, _("Invalid guess") + ".")
        return redirect("play", game_id=game_id)

    correct, misplaced = game_obj.check_guess(game_obj.code, guess)

    guess_obj = Guess(game=game_obj, guess=guess, correct=correct, misplaced=misplaced)
    guess_obj.save()

    if correct == 4:
        game_obj.won = True
        game_obj.save()
        messages.success(request, _("You won") + "!")
        return redirect("game", game_id=game_id)

    if guess_count == 9:
        messages.error(request, _("You lost") + ".")
        return redirect("game", game_id=game_id)

    return redirect("play", game_id=game_id)


def game(request: HttpRequest, game_id: int):
    try:
        game_obj = Game.objects.get(game_id=str(game_id).zfill(4))
    except Game.DoesNotExist:
        messages.error(request, _("Game does not exist") + ".")
        return redirect("mastermind")

    if not game_obj.is_finished():
        if game_obj.user == request.user:
            return redirect("play", game_id=game_id)

        messages.error(request, _("Game is not finished") + ".")
        return redirect("mastermind")

    if game_obj.won:
        messages.success(request, _("You won") + "!")
    else:
        messages.error(request, _("You lost") + ".")

    guesses = list(Guess.objects.filter(game=game_obj).order_by("created"))
    return render(
        request,
        "mastermind/game.html",
        {"game": game_obj, "guesses": guesses},
    )
