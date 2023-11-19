# Appu Wrote These
# Copyright (C) 2023  Appuchia <appuchia@appu.ltd>

from django.shortcuts import render


# Create your views here.
def home(request):
    return render(request, "mastermind/home.html")


def play(request):
    return render(request, "mastermind/play.html")
