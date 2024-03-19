# Appu Wrote These
# Copyright (C) 2023  Appuchia <appuchia@appu.ltd>

from datetime import date, timedelta
from typing import Iterable

from django.contrib import messages
from django.db.models import Count
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from gas import models

## DB name lookup ##
get_db_product_name = lambda prod_abbr, default="": {
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
}.get(prod_abbr, default)


## Get locality/province id ##
def get_ids(term: str) -> tuple[int, int]:
    """Gets the locality id, province id or postal code from the query"""

    if isinstance(term, str):
        # Look it up as a locality
        locality = models.Locality.objects.filter(name__iexact=term).first()
        if locality:
            return locality.id_mun, 0
        else:
            locality = models.Locality.objects.filter(name__icontains=term)
            if locality.exists():
                # Select locality with more stations
                locality = locality.annotate(num_stations=Count("station")).order_by(
                    "-num_stations"
                )[0]

                return locality.id_mun, 0

        province = models.Province.objects.filter(name__iexact=term.upper()).first()
        if not province:
            # Provinces are uppercase in the DB
            province = models.Province.objects.filter(name__icontains=term.upper())
            if province.exists():
                # Select province with more stations
                province = province.annotate(num_stations=Count("station")).order_by(
                    "-num_stations"
                )[0]

                return 0, province.id_prov
        else:
            return 0, province.id_prov

    return 0, 0


## Process the query form ##
def db_prices(
    term_id: int,
    term_type: str,
    prod_abbr: str,
    q_date: date,
) -> Iterable[models.StationPrice]:
    """Get the prices from the database.

    This function gets query data and returns the list of results.

    The term type must be one of (locality_id, province_id, postal_code)
    """

    station_filter = {f"station__{term_type}": term_id}

    prod_name = get_db_product_name(prod_abbr)
    prices = (
        models.StationPrice.objects.filter(date=q_date, **station_filter)
        .exclude(**{f"{prod_name}": None})
        .order_by(prod_name)
    )

    if not prices.exists():
        return list()

    return prices


def get_stations_prices(
    station_ids: int | Iterable[int], fuel: str, q_date: date
) -> Iterable[models.StationPrice]:
    """Get the prices from the database.

    This function gets the station id(s), the fuel used to sort the prices
    and the date and returns the list of prices.
    It accepts a single station id or an iterable of station ids.
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

    # Stores for each ideess if the price is higher, lower, equal or unknown
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
