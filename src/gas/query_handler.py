# Appu Wrote These
# Copyright (C) 2023  Appuchia <appuchia@appu.ltd>

from datetime import date, datetime, timedelta
from geopy.distance import distance
from typing import Iterable

from django.db.models import Count
from django.utils.translation import gettext_lazy as _

from gas.models import Locality, Province, Station, StationPrice

QUERY_LOG_FILE = "log/query_log.csv"


## Log queries ##
def log_query(fuel, q_date):
    try:
        with open(QUERY_LOG_FILE, "r") as f:
            pass
    except FileNotFoundError:
        with open(QUERY_LOG_FILE, "w") as f:
            f.write("datetime;fuel;q_date\n")

    with open(QUERY_LOG_FILE, "a") as f:
        f.write(f"{datetime.now().isoformat()};{fuel};{q_date}\n")


## Get locality/province id ##
def get_ids(term: str) -> tuple[int, int]:
    """Gets the locality id, province id or postal code from the query"""

    if isinstance(term, str):
        # Look it up as a locality
        locality = Locality.objects.filter(name__iexact=term).first()
        if locality:
            return locality.id_mun, 0
        else:
            locality = Locality.objects.filter(name__icontains=term)
            if locality.exists():
                # Select locality with more stations
                locality = locality.annotate(num_stations=Count("station")).order_by(
                    "-num_stations"
                )[0]

                return locality.id_mun, 0

        province = Province.objects.filter(name__iexact=term.upper()).first()
        if not province:
            # Provinces are uppercase in the DB
            province = Province.objects.filter(name__icontains=term.upper())
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
    term_id: int, term_type: str, prod_name: str, q_date: date
) -> Iterable[StationPrice]:
    """Get the prices from the database.

    This function gets query data and returns the list of results.

    The term type must be one of (locality_id, province_id, postal_code)
    """

    station_filter = {f"{term_type}": term_id}
    stations = Station.objects.filter(**station_filter)

    prices = (
        StationPrice.objects.filter(date=q_date, station__in=stations)
        .exclude(**{f"{prod_name}": None})
        .order_by(prod_name)
    )

    if not prices.exists():
        return list()

    return prices


def get_by_coords(
    latitude: float, longitude: float, radius: float, prod_name: str, q_date: date
) -> Iterable[StationPrice]:
    """Get the prices from the database.

    This function gets the coordinates, the radius, the fuel used to sort the prices
    and the date and returns the list of prices.

    The radius is in km.
    """
    # radius = radius / 111.12  # 1 degree is approximately 111.12 km

    # Approximate the bounding box
    src = (latitude, longitude)
    d = distance(kilometers=radius)
    north_lat = d.destination(src, 0).latitude
    south_lat = d.destination(src, 180).latitude
    east_lon = d.destination(src, -90).longitude
    west_lon = d.destination(src, 90).longitude

    # This will only work in the northern hemisphere (which is the case for Spain)
    stations = Station.objects.filter(
        latitude__range=(south_lat, north_lat),
        longitude__range=(west_lon, east_lon),
    )

    # Filter by distance
    stations = filter(
        lambda s: distance(src, (s.latitude, s.longitude)).kilometers <= radius,
        stations,
    )

    # Get the prices
    prices = (
        StationPrice.objects.filter(date=q_date, station__in=stations)
        .exclude(**{f"{prod_name}": None})
        .order_by(prod_name)
    )

    return prices


def get_stations_prices(
    station_ids: int | Iterable[int], prod_name: str, q_date: date
) -> Iterable[StationPrice]:
    """Get the prices from the database.

    This function gets the station id(s), the fuel used to sort the prices
    and the date and returns the list of prices.
    It accepts a single station id or an iterable of station ids.
    """

    if isinstance(station_ids, int):
        raw_prices = StationPrice.objects.filter(station_id=station_ids, date=q_date)
    else:
        raw_prices = StationPrice.objects.filter(
            station_id__in=station_ids, date=q_date
        )

    prices = raw_prices.exclude(**{f"{prod_name}": None}).order_by(prod_name)

    return prices


def get_station_prices_range(
    station_id: int, start_date: date, end_date: date
) -> list[StationPrice]:
    """Get the prices from the database.

    This function gets the station id, the start date and the end date and returns the list of prices.
    """

    prices = StationPrice.objects.filter(
        station_id=station_id, date__range=[start_date, end_date]
    ).order_by("date")

    return list(prices)


def are_past_prices_lower(
    curr_prices, prod_name: str, q_date: date, day_diff: int
) -> dict[int, str]:
    """Get the a past date's prices"""

    prev_week = q_date - timedelta(days=day_diff)
    past_prices = get_stations_prices(
        (price.station.id_eess for price in curr_prices), prod_name, prev_week
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
