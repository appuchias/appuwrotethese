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

from django.http import HttpRequest, JsonResponse
from django.utils.translation import gettext_lazy as _

from api.gas.handlers import format_prices
from gas.forms import GetPrices, SearchPrices
from gas.query_handler import db_prices, get_ids


def home(request: HttpRequest):
    """Home page for the Gas API."""

    return JsonResponse({"message": _("Welcome to the Gas API!")})


def get_prices(request: HttpRequest):
    """Get prices for a given locality ID, province ID or postal code."""

    form = GetPrices(request.GET)
    if not form.is_valid():
        return JsonResponse(
            {"message": _("Invalid request"), "errors": form.errors}, status=400
        )

    form_data = form.cleaned_data
    locality_id = form_data.get("locality_id")
    province_id = form_data.get("province_id")
    postal_code = form_data.get("postal_code")
    fuel_abbr = form_data.get("fuel_abbr")
    q_date = form_data.get("q_date")

    if not any((locality_id, province_id, postal_code)):
        return JsonResponse(
            {
                "message": _(
                    "You must provide a valid locality, province, or postal code."
                )
            },
            status=400,
        )

    prices = db_prices(
        request, locality_id, province_id, postal_code, fuel_abbr, q_date
    )

    return JsonResponse(format_prices(prices, fuel_abbr, q_date))


def search_prices(request: HttpRequest):
    """Search for prices for a given locality, province, or postal code."""

    form = SearchPrices(request.GET)
    if not form.is_valid():
        return JsonResponse(
            {"message": _("Invalid request"), "errors": form.errors}, status=400
        )

    form_data = form.cleaned_data
    term = form_data.get("term")
    q_type = form_data.get("q_type")
    fuel_abbr = form_data.get("fuel_abbr")
    q_date = form_data.get("q_date")

    locality_id, province_id, postal_code = get_ids(request, term, q_type)
    if not any((locality_id, province_id, postal_code)):
        return JsonResponse(
            {
                "message": _(
                    "You must provide a valid locality, province, or postal code."
                )
            },
            status=400,
        )

    prices = db_prices(
        request, locality_id, province_id, postal_code, fuel_abbr, q_date
    )

    return JsonResponse(format_prices(prices, fuel_abbr, q_date))
