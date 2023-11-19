# Appu Wrote These
# Copyright (C) 2023  Appuchia <appuchia@appu.ltd>

from django.urls import path

from mastermind import views

urlpatterns = [
    path("", views.home, name="home"),
]
