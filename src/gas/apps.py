# Appu Wrote These
# Copyright (C) 2023  Appuchia <appuchia@appu.ltd>

from django.apps import AppConfig
import requests

import threading
from appuwrotethese.extras import (
    store_json_data,
    FILEPATH_ROOT,
    PATH_PRODUCTS,
    PATH_LOCALITIES,
    PATH_PROVINCES,
)


##    Create aux. API files    ##
def fetch_products() -> list:
    """Get the products from the database.

    Format:
    [{
        "IDProducto":"Contenido de la cadena",
        "NombreProducto":"Contenido de la cadena",
        "NombreProductoAbreviatura":"Contenido de la cadena"
    }]
    """

    url = "https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/Listados/ProductosPetroliferos/"
    products = requests.get(url).json()
    return products


def fetch_localities() -> list:
    """Get the localities from the database.

    Format:
    [{
        "IDMunicipio":"Contenido de la cadena",
        "IDProvincia":"Contenido de la cadena",
        "IDCCAA":"Contenido de la cadena",
        "Municipio":"Contenido de la cadena",
        "Provincia":"Contenido de la cadena",
        "CCAA":"Contenido de la cadena"
    }]
    """

    url = "https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/Listados/Municipios/"
    localities = requests.get(url).json()
    return localities


def fetch_provinces() -> list:
    """Get the provinces from the database.

    Format:
    [{
        "IDPovincia":"Contenido de la cadena", # Mispelled in the API
        "IDCCAA":"Contenido de la cadena",
        "Provincia":"Contenido de la cadena",
        "CCAA":"Contenido de la cadena"
    }]
    """

    url = "https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/Listados/Provincias/"
    provinces = requests.get(url).json()

    return provinces


def create_files() -> None:
    """Create the files needed for the program."""

    # Create folders
    for folder in (FILEPATH_ROOT, FILEPATH_ROOT / "data"):
        if not folder.exists():
            folder.mkdir()

    # Create files
    relations = {
        PATH_PRODUCTS: fetch_products,
        PATH_LOCALITIES: fetch_localities,
        PATH_PROVINCES: fetch_provinces,
    }

    for path, fetch in relations.items():
        if not path.exists():
            store_json_data(fetch(), path)


class GasConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "gas"
    verbose_name = "Gasolineras"

    # Run code ONCE when started
    def ready(self) -> None:
        threading.Thread(target=create_files).start()
