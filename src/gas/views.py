# Appu Wrote These
# Copyright (C) 2023  Appuchia <appuchia@appu.ltd>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from datetime import date

from django.contrib import messages
from django.http import HttpRequest, HttpResponseNotAllowed
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from gas import forms, query_handler

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

    form = forms.SearchPrices(request.POST)
    if not form.is_valid():
        messages.error(request, _("Invalid form. Please try again."))
        return render(request, "gas/noresults.html", {"results": []})

    form_data = form.cleaned_data
    term = str(form_data.get("term"))
    q_type = str(form_data.get("q_type"))
    fuel_abbr = str(form_data.get("fuel_abbr"))
    q_date = form_data.get("q_date", date.today())

    id_locality, id_province, postal_code = query_handler.get_ids(request, term, q_type)
    prices = query_handler.db_prices(
        request, id_locality, id_province, postal_code, fuel_abbr, q_date
    )

    prices_date = form_data.get("q_date", date.today())
    if prices_date == date.today():
        prices_date = query_handler.get_last_update(form_data)

    if not request.user.is_authenticated:
        return render(
            request,
            "gas/results.html",
            {
                "results": prices,
                "term": form_data.get("term"),
                "fuel": FUEL_NAMES.get(form_data.get("fuel_abbr")),
                "date": prices_date,
            },
        )

    prod_name = query_handler.get_db_product_name(form_data.get("fuel_abbr"))
    prev_week_prices = query_handler.get_prev_week_prices(
        prices, form_data.get("fuel_abbr"), form_data.get("q_date")
    )

    prev_lower = {}
    for price in prices:
        if getattr(price, prod_name) > prev_week_prices.get(price.station.id_eess):
            prev_lower[price.station.id_eess] = 1
        elif getattr(price, prod_name) < prev_week_prices.get(price.station.id_eess):
            prev_lower[price.station.id_eess] = -1
        else:
            prev_lower[price.station.id_eess] = 0

    return render(
        request,
        "gas/results.html",
        {
            "results": prices,
            "term": form_data.get("term"),
            "fuel": FUEL_NAMES.get(form_data.get("fuel_abbr")),
            "date": prices_date,
            "prev_lower": prev_lower,
        },
    )
