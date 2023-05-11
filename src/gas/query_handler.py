import json
from datetime import datetime
from typing import Iterable

import requests
from django.contrib import messages
from django.db.models import Count
from django.http import HttpRequest, Http404
from django.utils.translation import gettext_lazy as _

from appuwrotethese.extras import PATH_DATA, PATH_PRODUCTS, get_json_data
from gas import models

LOCALITY_URL = "https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/FiltroMunicipioProducto/"
PROVINCE_URL = "https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/FiltroProvinciaProducto/"
ALL_URL = "https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/FiltroProducto/"


# ############################## #
#    Product id/name lookups     #
# ############################## #
def get_product_id(product_abbr: str) -> int:
    """Takes the short form of the product name and returns the API id"""

    products = get_json_data(PATH_PRODUCTS)
    for product in products:
        if product["NombreProductoAbreviatura"] == product_abbr:
            return int(product["IDProducto"])

    return 0


def get_db_product_name(prod_abbr: str) -> str:
    """Takes the short form of the product name and returns the full DB name"""

    return {
        "GOA": "gasoleo_a",
        "G95E5": "gasolina_95",
        "G98E5": "gasolina_98",
        "GLP": "glp",
    }.get(prod_abbr, "")


def get_product_name(product_abbr: str) -> str:
    """Takes the short form of the product name and returns the full name"""

    return {
        "GOA": "Gasóleo A",
        "G95E5": "Gasolina 95",
        "G98E5": "Gasolina 98",
        "GLP": "GLP",
    }.get(product_abbr, "Gasóleo A")


# ################## #
#    Make queries    #
# ################## #
def search_api(
    id_locality: int, id_province: int, postal_code: int, prod_abbr: str
) -> Iterable:
    """Gets the stations matching the query from the API"""

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


def search_db(
    id_locality: int, id_province: int, postal_code: int, prod_abbr: str
) -> Iterable:
    """Gets the stations matching the query from the database"""

    prod_name = get_db_product_name(prod_abbr)

    if id_locality:
        stations = models.Station.objects.filter(locality_id=id_locality)
    elif id_province:
        stations = models.Station.objects.filter(province_id=id_province)
    elif postal_code:
        stations = models.Station.objects.filter(postal_code=postal_code)
    else:
        return []

    stations = stations.exclude(**{f"{prod_name}": 0})

    return stations.order_by(prod_name)


# ############################ #
#    Process the query form    #
# ############################ #
def process_search(request: HttpRequest, form: dict) -> tuple[Iterable, str]:
    """Process a query and return the results.

    This function gets the request and the clean form data
    and returns the list of results and the product name (if needed).
    """

    query = str(form.get("query"))
    q_type = str(form.get("type"))
    prod_abbr = str(form.get("fuel"))
    show_all = bool(form.get("show_all", True))

    id_locality = 0
    id_province = 0
    postal_code = 0

    # Get the relevant IDs
    if q_type == "locality":
        locality = models.Locality.objects.filter(name__icontains=query)
        if locality.exists():
            # Select locality with more stations
            locality = locality.annotate(num_stations=Count("station")).order_by(
                "-num_stations"
            )[0]

            id_locality = locality.id_mun
        else:
            messages.add_message(request, messages.ERROR, _("Locality not found"))
            raise Http404

    elif q_type == "province":
        province = models.Province.objects.filter(name__icontains=query).first()
        if province:
            id_province = province.id_prov
        else:
            messages.add_message(request, messages.ERROR, _("Province not found"))
            raise Http404

    elif q_type == "postal_code":
        if query.isdigit() and len(query) == 5:
            postal_code = int(query)
        else:
            messages.add_message(
                request, messages.ERROR, _("Postal code invalid or not found")
            )
            raise Http404
    else:
        messages.add_message(request, messages.ERROR, _("Internal syntax error"))
        raise Http404

    return get_stations_prod_name(
        id_locality, id_province, postal_code, prod_abbr, show_all
    )


def get_stations_prod_name(
    id_locality: int, id_province: int, postal_code: int, prod_abbr: str, show_all: bool
) -> tuple[Iterable, str]:
    """Get the stations from the database or the API, provided all details."""

    if show_all:
        stations = search_db(id_locality, id_province, postal_code, prod_abbr)
    else:
        stations = search_api(id_locality, id_province, postal_code, prod_abbr)

    product_name = get_product_name(prod_abbr)

    return stations, product_name


def get_last_update(form_data) -> str:
    last_update = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    if form_data.get("show_all", True):
        with open(PATH_DATA, "r") as f:
            last_update = json.load(f).get("Fecha", last_update)

    return last_update
