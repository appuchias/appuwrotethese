# Appu Wrote These
# Copyright (C) 2023  Appuchia <appuchia@appu.ltd>

import json
from datetime import date, datetime, timedelta

from django.contrib import messages
from django.http import HttpRequest, HttpResponseNotAllowed
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from gas import models, forms, query_handler
from appuwrotethese.extras import PATH_DATA

FUEL_NAMES = {
    "GOA": "price_goa",
    "GOB": "price_gob",
    "G95E5": "price_g95e5",
    "G95E5+": "price_g95e5_premium",
    "G95E10": "price_g95e10",
    "G98E5": "price_g98e5",
    "G98E10": "price_g98e10",
    "GLP": "price_glp",
    "GNC": "price_gnc",
    "H2": "price_h2",
}


def search(request: HttpRequest):
    return render(request, "gas/search.html", {"form": forms.SearchPrices})


def result(request: HttpRequest):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"], "Method not allowed")

    hx = bool(request.headers.get("HX-Request", ""))

    form = forms.SearchPrices(request.POST)
    if not form.is_valid():
        error_msg = _("Invalid form. Please try again") + "."
        if not hx:
            messages.error(request, error_msg)
        return render(
            request, "gas/results.html", {"hx": hx, "results": [], "error": error_msg}
        )

    form_data = form.cleaned_data
    term = str(form_data.get("term"))
    fuel = form_data.get("fuel_abbr")
    q_date = form_data.get("q_date", date.today())

    if term.isdigit() and len(term) == 5:
        term_id = int(term)
        id_type = "postal_code"
    else:
        id_locality, id_province = query_handler.get_ids(term)
        if id_locality:
            term_id = id_locality
            id_type = "locality_id"
        elif id_province:
            term_id = id_province
            id_type = "province_id"
        else:
            error_msg = _("The location you're looking for could not be found") + "."
            if not hx:
                messages.error(request, error_msg)
            return render(
                request,
                "gas/results.html",
                {"hx": hx, "results": [], "error": error_msg},
            )

    prices = query_handler.db_prices(term_id, id_type, fuel, q_date)  # type: ignore

    if not prices:
        error_msg = (
            _("There were no prices in the database for that location and date") + "."
        )
        if not hx:
            messages.error(request, error_msg)
        return render(
            request,
            "gas/results.html",
            {"hx": hx, "results": [], "error": error_msg},
        )

    prices_date = form_data.get("q_date", date.today())
    if prices_date == date.today():
        with open(PATH_DATA, "r") as f:
            prices_date = json.load(f).get(
                "Fecha", datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            )

    past_day_lower = query_handler.are_past_prices_lower(prices, fuel, q_date, 1)  # type: ignore
    past_week_lower = query_handler.are_past_prices_lower(prices, fuel, q_date, 7)  # type: ignore
    past_month_lower = query_handler.are_past_prices_lower(prices, fuel, q_date, 30)  # type: ignore

    return render(
        request,
        "gas/results.html",
        {
            "hx": hx,
            "results": prices,
            "term": form_data.get("term"),
            "fuel": FUEL_NAMES.get(form_data.get("fuel_abbr")),  # type: ignore
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


def station(request: HttpRequest, id_eess: int):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"], "Method not allowed")

    station = models.Station.objects.get(id_eess=id_eess)
    currentprice = models.StationPrice.objects.filter(station=id_eess).latest("date")

    price_history = query_handler.get_station_prices_range(
        station.id_eess, date.today() - timedelta(days=60), date.today()
    )

    graph_data = [
        {
            "date": price.date,
            "price_goa": price.price_goa,
            "price_gob": price.price_gob,
            "price_g95e5": price.price_g95e5,
            "price_g98e5": price.price_g98e5,
            "price_glp": price.price_glp,
            "price_gnc": price.price_gnc,
            "price_h2": price.price_h2,
        }
        for price in price_history
    ]

    return render(
        request,
        "gas/station.html",
        {
            "station": station,
            "p": currentprice,
            "price_hist": price_history,
            "graph_data": graph_data,
        },
    )


# def station_pricerange(request: HttpRequest, id_eess: int):
#     if request.method != "GET":
#         return HttpResponseNotAllowed(["GET"], "Method not allowed")

#     start_date = request.GET.get("start_date", str(date.today() - timedelta(days=7)))
#     end_date = request.GET.get("end_date", str(date.today()))
#     start_date = date.fromisoformat(start_date)
#     end_date = date.fromisoformat(end_date)

#     station = models.Station.objects.get(id_eess=id_eess)
#     prices = query_handler.get_station_prices_range(id_eess, start_date, end_date)

#     daterangeform = forms.DateRangeForm(
#         initial={"start_date": start_date, "end_date": end_date}
#     )

#     return render(
#         request,
#         "gas/station_pricerange.html",
#         {"station": station, "prices": prices, "daterangeform": daterangeform},
#     )
