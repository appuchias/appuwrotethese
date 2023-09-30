# Appu Wrote These
# Copyright (C) 2023  Appuchia <appuchia@appu.ltd>

import json
from datetime import date, datetime

from django.contrib import messages
from django.http import HttpRequest, HttpResponseNotAllowed
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from gas import models, forms, query_handler

FUEL_NAMES = {
    "GOA": "diésel",
    "G95E5": "gasolina 95",
    "G98E5": "gasolina 98",
    "GLP": "gas licuado del petróleo",
}


def search(request: HttpRequest):
    return render(request, "gas/search.html", {"form": forms.SearchPrices})


def result(request: HttpRequest):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"], "Method not allowed")

    hx = bool(request.headers.get("HX-Request", ""))

    form = forms.SearchPrices(request.POST)
    if not form.is_valid():
        messages.error(request, _("Invalid form. Please try again."))
        return render(request, "gas/noresults.html", {"results": []})

    form_data = form.cleaned_data
    term = str(form_data.get("term"))
    q_type = str(form_data.get("q_type"))
    fuel = str(form_data.get("fuel_abbr"))
    q_date = form_data.get("q_date", date.today())

    id_locality, id_province, postal_code = query_handler.get_ids(term, q_type)
    if not any((id_locality, id_province, postal_code)):
        messages.error(request, _("No results found. Check your query and try again."))
        return render(request, "gas/noresults.html", {"results": []})
    prices = query_handler.db_prices(
        request, id_locality, id_province, postal_code, fuel, q_date
    )

    prices_date = form_data.get("q_date", date.today())
    if prices_date == date.today():
        with open(query_handler.PATH_DATA, "r") as f:
            prices_date = json.load(f).get(
                "Fecha", datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            )

    if not request.user.is_authenticated:
        return render(
            request,
            "gas/results.html",
            {
                "hx": hx,
                "results": prices,
                "term": form_data.get("term"),
                "fuel": FUEL_NAMES.get(form_data.get("fuel_abbr")),
                "date": prices_date,
            },
        )

    past_day_lower = query_handler.are_past_prices_lower(prices, fuel, q_date, 1)
    past_week_lower = query_handler.are_past_prices_lower(prices, fuel, q_date, 7)
    past_month_lower = query_handler.are_past_prices_lower(prices, fuel, q_date, 30)

    return render(
        request,
        "gas/results.html",
        {
            "hx": hx,
            "results": prices,
            "term": form_data.get("term"),
            "fuel": FUEL_NAMES.get(form_data.get("fuel_abbr")),
            "date": prices_date,
            "past_day_lower": past_day_lower,
            "past_week_lower": past_week_lower,
            "past_month_lower": past_month_lower,
        },
    )


def names(request: HttpRequest, **kwargs):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"], "Method not allowed")

    if kwargs.get("q_type") == "province":
        provinces = models.Province.objects.all()

        return render(
            request,
            "gas/names.html",
            {
                "names": [province.name for province in provinces],
                "q_type": _("Provinces"),
            },
        )

    localities = models.Locality.objects.all()

    return render(
        request,
        "gas/names.html",
        {
            "names": [locality.name for locality in localities],
            "q_type": _("Localities"),
        },
    )
