import json, requests
from datetime import datetime

from appuwrotethese.extras import (
    get_json_data,
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


def fetch_data() -> dict:
    """Get the data from the most recent source (file or remote).

    If the file is older than 30 minutes, redownload it.
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

        # Store the newly obtained data to a file
        with open(PATH_DATA, "w") as w:
            json.dump(data, w, indent=4, ensure_ascii=True)

    return data


# ########################### #
#    Create aux. API files    #
# ########################### #


def create_files() -> None:
    """Create the files needed for the program."""

    # Create folders
    for folder in (FILEPATH_ROOT, FILEPATH_ROOT / "data"):
        if not folder.exists():
            folder.mkdir()

    # Create files
    for path in (PATH_LOCALITIES, PATH_PROVINCES, PATH_PRODUCTS):
        if not path.exists():
            get_json_data(path)
