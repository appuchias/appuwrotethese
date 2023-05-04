import requests
from django.http import HttpRequest
from django.contrib import messages
from django.db.models import Count
from django.utils.translation import gettext_lazy as _
from typing import Iterable

from appuwrotethese.extras import get_user, get_json_data, PATH_PRODUCTS
from gas import models


# ############################## #
#    Product id/name lookups     #
# ############################## #


def get_product_id(product_abbr: str) -> int:
    products = get_json_data(PATH_PRODUCTS)
    for product in products:
        if product["NombreProductoAbreviatura"] == product_abbr:
            return int(product["IDProducto"])

    return 0


def get_db_product_name(prod_abbr: str) -> str:
    """Takes the short form of the product name and returns the full DB name"""
    products = {
        "GOA": "gasoleo_a",
        "G95E5": "gasolina_95",
        "G98E5": "gasolina_98",
        "GLP": "glp",
    }

    return products.get(prod_abbr, "")


# ###################### #
#    Make API queries    #
# ###################### #
def search_api(
    id_locality: int, id_province: int, postal_code: int, prod_abbr: str
) -> Iterable:
    """Gets the stations matching the query from the API"""

    id_prod = get_product_id(prod_abbr)

    if id_locality:
        url = f"https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/FiltroMunicipioProducto/{id_locality}/{id_prod}"
    elif id_province:
        url = f"https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/FiltroProvinciaProducto/{id_province}/{id_prod}"
    elif postal_code:
        url = f"https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/FiltroProducto/{id_prod}"
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


# ##################### #
#    Make DB queries    #
# ##################### #
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


def process_search(request: HttpRequest, form: dict) -> Iterable:
    """
    Process a query and return the results.

    This function gets the request and the clean form data
    and returns the list of results.
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
            return []

    elif q_type == "province":
        province = models.Province.objects.filter(name__icontains=query)
        if province.exists():
            # Select province with more stations
            province = province.annotate(num_stations=Count("station")).order_by(
                "-num_stations"
            )[0]

            id_province = province.id_prov
        else:
            messages.add_message(request, messages.ERROR, _("Province not found"))
            return []

    elif q_type == "postal_code":
        if query.isdigit() and len(query) == 5:
            postal_code = int(query)
        else:
            messages.add_message(
                request, messages.ERROR, _("Postal code invalid or not found")
            )
            return []
    else:
        messages.add_message(request, messages.ERROR, _("Internal syntax error"))
        return []

    if show_all:
        stations = search_db(id_locality, id_province, postal_code, prod_abbr)
    else:
        stations = search_api(id_locality, id_province, postal_code, prod_abbr)

    return stations


# def process_star(request, form_data) -> None:
#     from accounts.models import AWTUser

#     user = get_user(request)

#     if form_data["star"]:
#         if isinstance(user, AWTUser) and user.is_upgraded:
#             AWTUser.objects.filter(id=user.id).update(
#                 saved_query={
#                     "query": form_data["query"],
#                     "type": form_data["type"],
#                     "fuel": form_data["fuel"],
#                 }
#             )
#             messages.success(request, _("Query saved"))
#         else:
#             messages.error(request, _("Your account must be upgraded to save a query"))
