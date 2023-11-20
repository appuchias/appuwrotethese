# Appu Wrote These
# Copyright (C) 2023  Appuchia <appuchia@appu.ltd>

from django.urls import path

from mastermind import views

urlpatterns = [
    path("", views.home, name="home"),
    path("play/", views.play, name="play"),
    path("play/<int:game_id>/", views.play, name="play"),
    path("guess/", views.guess, name="guess"),
    path("game/<int:game_id>/", views.game, name="game"),
]
