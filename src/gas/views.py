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

FUEL_NAMES = dict(forms.FUEL_CHOICES)


def search(request: HttpRequest, geo: bool = False):
    form = forms.SearchPricesGeo() if geo else forms.SearchPrices()
    return render(request, "gas/search.html", {"form": form, "geo": geo})


def result(request: HttpRequest):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"], "Method not allowed")

    hx = bool(request.headers.get("HX-Request", ""))

    form = forms.SearchPrices(request.GET)
    if not form.is_valid():
        error_msg = _("Invalid form. Please try again") + "."
        if not hx:
            messages.error(request, error_msg)
        return render(
            request, "gas/results.html", {"hx": hx, "results": [], "error": error_msg}
        )

    form_data = form.cleaned_data
    term = str(form_data.get("term"))
    fuel = form_data.get("fuel_abbr", "GOA")
    q_date = form_data.get("q_date", date.today())

    # Log anonymized query
    query_handler.log_query(fuel, q_date)

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
            "fuel": FUEL_NAMES.get(fuel),
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
    if request.method not in ["GET", "POST"]:
        return HttpResponseNotAllowed(["GET", "POST"], "Method not allowed")

    def build_graph_data(price_history):
        return [
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

    if request.method == "POST":
        form = forms.DateRangeForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data.get(
                "start_date", date.today() - timedelta(days=30)
            )
            end_date = form.cleaned_data.get("end_date", date.today())

            return render(
                request,
                "gas/station_pricerange.html",
                {
                    "graph_data": build_graph_data(
                        query_handler.get_station_prices_range(
                            id_eess, start_date, end_date
                        )
                    ),
                },
            )

    station = models.Station.objects.get(id_eess=id_eess)
    currentprice = models.StationPrice.objects.filter(station=id_eess).latest("date")

    price_history = query_handler.get_station_prices_range(
        station.id_eess, date.today() - timedelta(days=60), date.today()
    )

    return render(
        request,
        "gas/station.html",
        {
            "station": station,
            "p": currentprice,
            "price_hist": price_history,
            "daterange_form": forms.DateRangeForm(),
            "graph_data": build_graph_data(price_history),
        },
    )


def result_geo(request: HttpRequest):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"], "Method not allowed")

    hx = bool(request.headers.get("HX-Request", ""))
    assert hx, "This view is only for HX-Requests (I think)"

    form = forms.SearchPricesGeo(request.GET)
    if not form.is_valid():
        return render(request, "gas/results.html", {"hx": hx, "results": []})

    form_data = form.cleaned_data

    lat = float(form_data.get("latitude", 0.0))
    lon = float(form_data.get("longitude", 0.0))
    radius = float(form_data.get("radius", 5.0))
    fuel = form_data.get("fuel_abbr", "GOA")
    q_date = form_data.get("q_date", date.today())

    # Log anonymized query
    query_handler.log_query(fuel, q_date)

    prices = query_handler.get_by_coords(lat, lon, radius, fuel, date.today())

    past_day_lower = query_handler.are_past_prices_lower(prices, fuel, q_date, 1)  # type: ignore
    past_week_lower = query_handler.are_past_prices_lower(prices, fuel, q_date, 7)  # type: ignore
    past_month_lower = query_handler.are_past_prices_lower(prices, fuel, q_date, 30)  # type: ignore

    return render(
        request,
        "gas/results.html",
        {
            "hx": hx,
            "results": prices,
            "term": f"{lat}, {lon}, {radius} km",
            "fuel": FUEL_NAMES.get(fuel),
            "date": q_date,
            "past_day_lower": past_day_lower,
            "past_week_lower": past_week_lower,
            "past_month_lower": past_month_lower,
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
