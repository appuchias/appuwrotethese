# Appu Wrote These
# Copyright (C) 2023  Appuchia <appuchia@appu.ltd>

from django.utils.translation import gettext as _
from django.http import HttpRequest, JsonResponse


def home(request: HttpRequest):
    """Home page for the API."""

    return JsonResponse({"path": _("Welcome to the API!")})


def health(request: HttpRequest):
    """Health check endpoint."""

    return JsonResponse({"status": "OK"})
