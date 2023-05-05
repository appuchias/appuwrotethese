from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from datetime import datetime
import json

from appuwrotethese import extras
from gas import forms, query_handler


def search(request: HttpRequest):
    return render(
        request,
        "gas/search.html",
        {
            "form": forms.SearchStations,
        },
    )


def result(request: HttpRequest):
    form = forms.SearchStations(request.POST)

    if request.method != "POST":
        # Using the HttpResponseNotAllowed would be better, but this is user
        # frieldier for a webpage without an API
        # return HttpResponseNotAllowed(["POST"], "Method not allowed")

        messages.error(request, _("Only POST is allowed in /gas/result/"))
        return redirect("/gas/")

    if form.is_valid():
        form_data = form.cleaned_data

        # helper_query.process_star(request, form_data)

        results = query_handler.process_search(request, form_data)
        product_name = {
            "GOA": "Gasóleo A",
            "G95E5": "Gasolina 95",
            "G98E5": "Gasolina 98",
            "GLP": "GLP",
        }.get(form_data.get("fuel", "GOA"), "Gasóleo A")
        last_update = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        if form_data.get("show_all", True):
            with open("gas/data/data.json", "r") as f:
                last_update = json.load(f).get("Fecha", last_update)

        # Show notification in case no results are returned
        if not results:
            messages.error(request, _("No results found"))
            return redirect("/gas/")

        return render(
            request,
            "gas/results.html",
            {
                "product": product_name,
                "results": results,
                "last_update": last_update,
            },
        )
    else:  # Form is not valid
        return render(
            request,
            "gas/noresults.html",
            {
                "error": _("Invalid form data. Please try again."),
            },
        )


def account(request: HttpRequest):
    user = extras.get_user(request)
    return render(
        request,
        "gas/account.html",
        {"awtuser": user},
    )


# def save(request: HttpRequest, id: int):
#     user = extras.get_user(request)
#     if user.is_authenticated and user.is_upgraded:
#         station = models.Station.objects.get(id_eess=id)
#         if not station:
#             messages.error(request, _("Station not found"))
#             return redirect("/account")
#         AWTUser.objects.filter(id=user.id).update(saved_station=station)
#         messages.success(request, _("Station saved"))
#     else:
#         messages.error(request, _("Your account must be upgraded to save a station"))
#         return redirect("/account")
#     return redirect("/gas")
