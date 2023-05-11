from django.utils.translation import gettext as _
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render, redirect
import os

from .settings import STATIC_ROOT


def home(request: HttpRequest):
    return render(request, "home.html")


def projects(request: HttpRequest):
    return redirect("/gas/")

    project_id = request.GET.get("id", "")
    projects = [
        {
            "project_id": 1,
            "name": _("Fuel prices"),
            "description": _(
                "A project where you can check the different prices of all gas stations in Spain to sort them from lowest to highest"
            )
            + ".",
            "url": "gas/",
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


def thanks(request: HttpRequest):
    return render(request, "thanks.html")


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


def redirect_static(request: HttpRequest, **kwargs):
    dest = kwargs.get("resource", "")

    if dest and os.path.isfile(STATIC_ROOT / dest):
        return redirect(f"/s/{dest}")

    return redirect("/")


def health(request: HttpRequest):
    return JsonResponse({"status": "ok"})


def handler404(request: HttpRequest, exception):
    return render(request, "e404.html", status=404)


def handler500(request: HttpRequest):
    return render(request, "e500.html", status=500)
