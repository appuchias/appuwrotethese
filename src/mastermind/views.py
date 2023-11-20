# Appu Wrote These
# Copyright (C) 2023  Appuchia <appuchia@appu.ltd>

from django import forms
from django.contrib import messages
from django.http import HttpRequest, HttpResponseNotAllowed
from django.shortcuts import render, redirect

from mastermind.models import Game, Guess
from mastermind.forms import MastermindGuess

validate_guess = lambda guess: (
    len(set(str(guess))) == 4 and all(digit in "0123456789" for digit in str(guess))
)


def home(request: HttpRequest):
    return render(request, "mastermind/home.html")


def play(request: HttpRequest, game_id: int | None = None):
    if not game_id:
        game_obj = Game()
        game_obj.save()

        game_id = Game.objects.latest("game_id").game_id

        return redirect("play", game_id=game_id)

    try:
        game_obj = Game.objects.get(game_id=str(game_id).zfill(4))
    except Game.DoesNotExist:
        messages.error(request, "Game does not exist.")
        return redirect("home")

    if game_obj.is_finished():
        messages.error(request, "Game is finished.")
        return redirect("game", game_id=game_id)

    form = MastermindGuess()
    form.fields["game_id"].initial = game_id

    guesses = list(Guess.objects.filter(game=game_obj).order_by("created"))
    return render(
        request,
        "mastermind/play.html",
        {"game": game_obj, "guesses": guesses, "form": form},
    )


def guess(request: HttpRequest):
    allowed_methods = ["POST"]
    if request.method not in allowed_methods:
        return HttpResponseNotAllowed(allowed_methods)

    form = MastermindGuess(request.POST)
    if not form.is_valid():
        messages.error(request, "Invalid form.")
        return redirect("home")

    game_id = form.cleaned_data["game_id"]
    guess = form.cleaned_data["guess"]

    game_obj = Game.objects.get(game_id=str(game_id).zfill(4))
    guess_count = game_obj.get_guess_count()

    if guess_count >= 10:
        messages.error(request, "You have used all your guesses.")
        return redirect("home")

    if not validate_guess(guess):
        messages.error(request, "Invalid guess.")
        return redirect("play", game_id=game_id)

    correct, misplaced = game_obj.check_guess(game_obj.code, str(guess))

    guess_obj = Guess(
        game=game_obj,
        guess=str(guess),
        correct=correct,
        misplaced=misplaced,
    )
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
        return redirect("play")

    if not game_obj.is_finished():
        messages.error(request, "Game is not finished.")
        return redirect("play")

    guesses = list(Guess.objects.filter(game=game_obj).order_by("created"))
    return render(
        request,
        "mastermind/game.html",
        {"game": game_obj, "guesses": guesses},
    )
