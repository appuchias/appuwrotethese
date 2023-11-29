# Appu Wrote These
# Copyright (C) 2023  Appuchia <appuchia@appu.ltd>

from django.shortcuts import render
from django.http import HttpRequest

def quickcalc(request: HttpRequest):
    return render(request, "quickcalc/quickcalc.html")
