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

import json
from datetime import date, datetime, timedelta
from typing import Iterable

from django.contrib import messages
from django.db.models import Count
from django.http import Http404, HttpRequest
from django.utils.translation import gettext_lazy as _

from appuwrotethese.extras import PATH_DATA
from gas import models

## DB name lookup ##
get_db_product_name = lambda prod_abbr, default="": {
    "GOA": "price_goa",
    "G95E5": "price_g95e5",
    "G98E5": "price_g98e5",
    "GLP": "price_glp",
}.get(prod_abbr, default)


## Get locality id/province id/postal code ##
def get_ids(query: str, q_type: str) -> tuple[int, int, int]:
    """Gets the locality id, province id or postal code from the query"""

    id_locality = 0
    id_province = 0
    postal_code = 0

    if q_type == "locality":
        locality = models.Locality.objects.filter(name__iexact=query).first()
        if not locality:
            locality = models.Locality.objects.filter(name__icontains=query)
            if locality.exists():
                # Select locality with more stations
                locality = locality.annotate(num_stations=Count("station")).order_by(
                    "-num_stations"
                )[0]

                id_locality = locality.id_mun
        else:
            id_locality = locality.id_mun

    elif q_type == "province":
        province = models.Province.objects.filter(name__iexact=query.upper()).first()
        if not province:
            # Provinces are uppercase in the DB
            province = models.Province.objects.filter(name__icontains=query.upper())
            if province.exists():
                # Select province with more stations
                province = province.annotate(num_stations=Count("station")).order_by(
                    "-num_stations"
                )[0]

                id_province = province.id_prov
        else:
            id_province = province.id_prov

    elif q_type == "postal_code":
        if query.isdigit() and len(query) == 5:
            postal_code = int(query)

    return id_locality, id_province, postal_code


## Process the query form ##
def db_prices(
    request: HttpRequest,
    id_locality: int,
    id_province: int,
    postal_code: int,
    prod_abbr: str,
    q_date: date,
) -> Iterable[models.StationPrice]:
    """Get the prices from the database.

    This function gets the request and the clean form data
    and returns the list of results.

    You must pass either id_locality, id_province or postal_code.
    If more than one is passed, the first one (in that order) will be used.
    """

    if id_locality:
        station_filter = {"locality_id": id_locality}
    elif id_province:
        station_filter = {"province_id": id_province}
    elif postal_code:
        station_filter = {"postal_code": postal_code}
    else:
        return []

    stations = models.Station.objects.filter(**station_filter)

    if not stations.exists():
        messages.error(request, _("No stations found in the selected area."))
        return []

    prod_name = get_db_product_name(prod_abbr)
    prices = (
        models.StationPrice.objects.filter(station__in=stations, date=q_date)
        .exclude(**{f"{prod_name}": None})
        .order_by(prod_name)
    )

    if not prices.exists():
        messages.error(request, _("No prices were found. Try with a broader search."))
        return []

    return prices


def get_stations_prices(
    station_ids: int | Iterable[int], fuel: str, q_date: date
) -> Iterable[models.StationPrice]:
    """Get the prices from the database.

    This function gets the request and the clean form data
    and returns the list of results
    """

    prod_name = get_db_product_name(fuel)

    if isinstance(station_ids, int):
        raw_prices = models.StationPrice.objects.filter(
            station_id=station_ids, date=q_date
        )
    else:
        raw_prices = models.StationPrice.objects.filter(
            station_id__in=station_ids, date=q_date
        )

    prices = raw_prices.exclude(**{f"{prod_name}": None}).order_by(prod_name)

    return prices


def are_past_prices_lower(
    curr_prices, fuel: str, q_date: date, day_diff: int
) -> dict[int, str]:
    """Get the a past date's prices"""

    prev_week = q_date - timedelta(days=day_diff)
    prod_name = get_db_product_name(fuel)
    past_prices = get_stations_prices(
        (price.station.id_eess for price in curr_prices), fuel, prev_week
    )
    past_prices = {
        price.station.id_eess: getattr(price, prod_name) for price in past_prices
    }

    prev_lower = {}
    for price in curr_prices:
        if not past_prices.get(price.station.id_eess):
            prev_lower[price.station.id_eess] = "u"
            continue

        if getattr(price, prod_name) > past_prices.get(price.station.id_eess):
            prev_lower[price.station.id_eess] = "l"
        elif getattr(price, prod_name) < past_prices.get(price.station.id_eess):
            prev_lower[price.station.id_eess] = "h"
        else:
            prev_lower[price.station.id_eess] = "e"

    return prev_lower


def get_last_update(form_data) -> str:
    last_update = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    if form_data.get("show_all", True):
        with open(PATH_DATA, "r") as f:
            last_update = json.load(f).get("Fecha", last_update)

    return last_update
