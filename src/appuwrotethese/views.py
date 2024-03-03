# Appu Wrote These
# Copyright (C) 2023  Appuchia <appuchia@appu.ltd>

from django.utils.translation import gettext as _
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render, redirect
import os

from .settings import STATIC_ROOT


def home(request: HttpRequest):
    return render(request, "home.html")


def projects(request: HttpRequest):
    project_id = request.GET.get("id", "")
    projects = [
        {
            "project_id": 1,
            "name": _("Fuel prices"),
            "description": _("Find the cheapest gas prices") + ".",
            "url": "gas/",
        },
        {
            "project_id": 2,
            "name": _("Mastermind"),
            "description": _("Play the Mastermind game") + "!",
            "url": "mastermind/",
        },
        {
            "project_id": 1,
            "name": _("Future"),
            "description": _("Future projects") + "...",
            "url": "projects/#",
        },
    ]

    def no_project(request: HttpRequest):
        return render(
            request,
            "projects.html",
            {"project_list": projects},
        )

    if project_id:
        try:
            if project_id.isdigit():
                project_id = int(project_id)
            else:
                return no_project(request)

            project = projects[project_id - 1]
        except IndexError:
            project = {
                "name": _("Project placeholder #") + str(project_id),
                "project_id": project_id,
                "url": "build/",
                "description": _("Placeholder project description"),
            }
        return render(
            request,
            "project.html",
            {"project": project},
        )
    else:
        return no_project(request)


def health(request: HttpRequest):
    """Health check endpoint."""

    return JsonResponse({"status": "OK"})


def legal(request: HttpRequest):
    return render(request, "legal.html")


def text(request: HttpRequest):
    title = request.GET.get("title", "Appuchia")
    text = request.GET.get("text", "-")
    return render(
        request,
        "text.html",
        {"title": title, "text": text},
    )


def build(request: HttpRequest):
    return render(request, "build.html")


def teapot(request: HttpRequest):
    return render(request, "teapot.html", status=418)


def redirect_static(request: HttpRequest, **kwargs):
    dest = kwargs.get("resource", "")

    if dest and os.path.isfile(STATIC_ROOT / dest):
        return redirect(f"/s/{dest}", permanent=True)

    return redirect("/")


def handler404(request: HttpRequest, exception):
    return render(request, "404.html", status=404)


def handler500(request: HttpRequest):
    return render(request, "500.html", status=500)
