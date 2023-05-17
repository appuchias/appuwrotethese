import json
from datetime import date, datetime
from typing import Iterable

import requests
from django.db.models import Count
from django.http import Http404, HttpRequest
from django.utils.translation import gettext_lazy as _

from appuwrotethese.extras import PATH_DATA
from gas import models


## DB name lookup ##
def get_db_product_name(prod_abbr: str, default: str = "") -> str:
    """Takes the short form of the product name and returns the full DB name"""

    return {
        "GOA": "price_goa",
        "G95E5": "price_g95",
        "G98E5": "price_g98",
        "GLP": "price_glp",
    }.get(prod_abbr, default)


## Long name lookup ##
def get_product_name(product_abbr: str, default: str = "") -> str:
    """Takes the short form of the product name and returns the full name"""

    return {
        "GOA": "Gasóleo A",
        "G95E5": "Gasolina 95",
        "G98E5": "Gasolina 98",
        "GLP": "GLP",
    }.get(product_abbr, default)


## Get locality id/province id/postal code ##
def get_ids(query: str, q_type: str) -> tuple[int, int, int]:
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
            raise Http404

    elif q_type == "province":
        province = models.Province.objects.filter(name__icontains=query).first()
        if province:
            id_province = province.id_prov
        else:
            raise Http404

    elif q_type == "postal_code":
        if query.isdigit() and len(query) == 5:
            postal_code = int(query)
        else:
            raise Http404

    return id_locality, id_province, postal_code

    id_prod = get_product_id(prod_abbr)

    if id_locality:
        url = LOCALITY_URL + f"{id_locality}/{id_prod}"
    elif id_province:
        url = PROVINCE_URL + f"{id_province}/{id_prod}"
    elif postal_code:
        url = ALL_URL + f"{id_prod}"
    else:
        return []

    stations = requests.get(url).json()["ListaEESSPrecio"]

    if postal_code:
        stations = [
            station for station in stations if int(station["C.P."]) == postal_code
        ]

    changes = {
        "Dirección": "address",
        "Horario": "schedule",
        "Rótulo": "company",
        "IDEESS": "id_eess",
        "Latitud": "latitude",
        "Longitud (WGS84)": "longitude",
        "Municipio": "locality",
        "Provincia": "province",
        "C.P.": "postal_code",
    }
    for station in stations:
        for key, value in changes.items():
            station[value] = station.pop(key)

    return sorted(stations, key=lambda x: x["PrecioProducto"])


## Process the query form ##
def process_search(request: HttpRequest, form: dict) -> tuple[Iterable, str]:
    """Process a query and return the results.

    This function gets the request and the clean form data
    and returns the list of results and the product name.
    """

    query = str(form.get("query"))
    q_type = str(form.get("type"))
    prod_abbr = str(form.get("fuel"))

    id_locality, id_province, postal_code = get_ids(query, q_type)

    return get_stations_prod_name(id_locality, id_province, postal_code, prod_abbr)


def get_stations_prod_name(
    id_locality: int, id_province: int, postal_code: int, prod_abbr: str
) -> tuple[Iterable, str]:
    """Get the stations from the database or the API, provided all details."""

    prod_name = get_db_product_name(prod_abbr)

    if id_locality:
        station_filter = {"locality_id": id_locality}
    elif id_province:
        station_filter = {"province_id": id_province}
    elif postal_code:
        station_filter = {"postal_code": postal_code}
    else:
        return [], prod_name

    stations = models.Station.objects.filter(**station_filter)

    prices = (
        models.StationPrice.objects.filter(station__in=stations, date=date.today())
        .exclude(**{f"{prod_name}": 0})
        .order_by(f"{prod_name}")
    )

    return prices, prod_name


def get_last_update(form_data) -> str:
    last_update = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    if form_data.get("show_all", True):
        with open(PATH_DATA, "r") as f:
            last_update = json.load(f).get("Fecha", last_update)

    return last_update
