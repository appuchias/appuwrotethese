# Appu Wrote These
# Copyright (C) 2023  Appuchia <appuchia@appu.ltd>

from django.urls import path

from mastermind import views

urlpatterns = [
    path("", views.mastermind, name="mastermind"),
    path("play/", views.play, name="play"),
    path("play/<str:game_id>/", views.play, name="play"),
    path("guess/<str:game_id>/", views.guess, name="guess"),
    path("game/<str:game_id>/", views.game, name="game"),
]
