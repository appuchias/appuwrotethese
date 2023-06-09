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
from datetime import date, datetime
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
def get_ids(request: HttpRequest, query: str, q_type: str) -> tuple[int, int, int]:
    """Gets the locality id, province id or postal code from the query"""

    id_locality = 0
    id_province = 0
    postal_code = 0

    if q_type == "locality":
        locality = models.Locality.objects.filter(name__icontains=query)
        if locality.exists():
            # Select locality with more stations
            locality = locality.annotate(num_stations=Count("station")).order_by(
                "-num_stations"
            )[0]

            id_locality = locality.id_mun
        else:
            messages.error(request, _("Locality not found"))
            raise Http404

    elif q_type == "province":
        province = models.Province.objects.filter(name__icontains=query).first()
        if province:
            id_province = province.id_prov
        else:
            messages.error(request, _("Province not found"))
            raise Http404

    elif q_type == "postal_code":
        if query.isdigit() and len(query) == 5:
            postal_code = int(query)
        else:
            messages.error(request, _("Invalid postal code"))
            raise Http404

    return id_locality, id_province, postal_code


## Process the query form ##
def process_search(request: HttpRequest, form: dict) -> Iterable[models.StationPrice]:
    """Process a query and return the results.

    This function gets the request and the clean form data
    and returns the list of results and the product name.
    """

    term = str(form.get("term"))
    q_type = str(form.get("q_type"))
    fuel_abbr = str(form.get("fuel_abbr"))
    q_date = form.get("q_date", date.today())

    id_locality, id_province, postal_code = get_ids(request, term, q_type)

    return db_prices(request, id_locality, id_province, postal_code, fuel_abbr, q_date)


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
    and returns the list of results
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
        .order_by(f"{prod_name}")
    )

    if not prices.exists():
        messages.error(
            request, _("No prices found. Date may be missing or no sations were found.")
        )
        return []

    return prices


def get_last_update(form_data) -> str:
    last_update = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    if form_data.get("show_all", True):
        with open(PATH_DATA, "r") as f:
            last_update = json.load(f).get("Fecha", last_update)

    return last_update
