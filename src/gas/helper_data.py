import json, requests
from datetime import datetime

from appuwrotethese.extras import (
    get_json_data,
    store_json_data,
    DATA_OLD_MINUTES,
    FILEPATH_ROOT,
    PATH_PRODUCTS,
    PATH_LOCALITIES,
    PATH_PROVINCES,
    PATH_DATA,
)


# ######################### #
#  Data fetching functions  #
# ######################### #


def fetch_products() -> list:
    """
    Get the products from the database.
    """

    url = "https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/Listados/ProductosPetroliferos/"
    products = requests.get(url).json()

    # [{
    # "IDProducto":"Contenido de la cadena",
    # "NombreProducto":"Contenido de la cadena",
    # "NombreProductoAbreviatura":"Contenido de la cadena"
    # }]

    store_json_data(products, PATH_PRODUCTS)

    return products


def fetch_localities() -> list:
    """
    Get the localities from the database.
    """

    url = "https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/Listados/Municipios/"
    localities = requests.get(url).json()

    # [{
    # "IDMunicipio":"Contenido de la cadena",
    # "IDProvincia":"Contenido de la cadena",
    # "IDCCAA":"Contenido de la cadena",
    # "Municipio":"Contenido de la cadena",
    # "Provincia":"Contenido de la cadena",
    # "CCAA":"Contenido de la cadena"
    # }]

    store_json_data(localities, PATH_LOCALITIES)

    return localities


def fetch_provinces() -> list:
    """
    Get the provinces from the database.
    """

    url = "https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/Listados/Provincias/"
    provinces = requests.get(url).json()

    # [{
    # "IDPovincia":"Contenido de la cadena", # Mispelled in the API
    # "IDCCAA":"Contenido de la cadena",
    # "Provincia":"Contenido de la cadena",
    # "CCAA":"Contenido de la cadena"
    # }]

    store_json_data(provinces, PATH_PROVINCES)

    return provinces


def fetch_data() -> dict:
    """
    Get the data from the most recent source (file or remote).
    If file is older than 30 minutes, refresh it.
    """

    # Get the data from the file or fake its existence
    try:
        with open(PATH_DATA, "r") as r:
            data = json.load(r)
    except FileNotFoundError:
        # Fake the data exists and is obviously old
        data = {
            "Fecha": f"{str(datetime.fromtimestamp(0).strftime(r'%d/%m/%Y %H:%M:%S'))}"
        }

    # Determine if the data is old
    try:
        date = data["Fecha"]
    except KeyError:
        data_is_old = True
    else:
        data_time = datetime.strptime(date, "%d/%m/%Y %H:%M:%S")
        data_old_s = DATA_OLD_MINUTES * 60
        # True if data is older than DATA_OLD_MINUTES minutes
        data_is_old = (datetime.now() - data_time).total_seconds() > data_old_s

    # Refresh the data
    if data_is_old:
        print("[!] Data was old, refreshing...")
        data = requests.get(
            "https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/"
        ).json()

    # Store the obtained data to a file
    with open(PATH_DATA, "w") as w:
        json.dump(data, w, indent=4, ensure_ascii=True)

    return data


# ############### #
#   Get from fp   #
# ############### #


def get_products() -> dict:
    """Get the products from the file."""
    return get_json_data(PATH_PRODUCTS)


def get_localities() -> dict:
    """Get the localities from the file."""
    return get_json_data(PATH_LOCALITIES)


def get_provinces() -> dict:
    """Get the provinces from the file."""
    return get_json_data(PATH_PROVINCES)


# ####################### #
#    Startup functions    #
# ####################### #


def create_files() -> None:
    """
    Create the files needed for the program.
    """

    # Create folders
    for folder in (FILEPATH_ROOT, FILEPATH_ROOT / "data"):
        if not folder.exists():
            folder.mkdir()

    # Create files
    for path in (PATH_LOCALITIES, PATH_PROVINCES, PATH_PRODUCTS):
        if not path.exists():
            get_json_data(path)
