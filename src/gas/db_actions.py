from datetime import date, datetime
import django.utils.timezone as timezone
import json, requests

from appuwrotethese.extras import (
    get_json_data,
    DATA_OLD_MINUTES,
    PATH_DATA,
    PATH_LOCALITIES,
    PATH_PROVINCES,
)
from gas.models import Locality, Province, Station, StationPrice

# Change the field names to match the ones in the model
DB_FIELD_RENAME = {
    "IDEESS": "id_eess",
    "Dirección": "address",
    "Horario": "schedule",
    "Rótulo": "company",
    "Latitud": "latitude",
    "Longitud (WGS84)": "longitude",
    "C.P.": "postal_code",
}
DB_FIELD_REMOVE = [
    "Localidad",
    "Municipio",
    "Provincia",
    "Margen",
    "Precio Biodiesel",
    "Precio Bioetanol",
    "Precio Gas Natural Comprimido",
    "Precio Gas Natural Licuado",
    "Precio Gasoleo B",
    "Precio Gasoleo Premium",
    "Precio Gasolina 95 E10",
    "Precio Gasolina 95 E5 Premium",
    "Precio Gasolina 98 E10",
    "Precio Hidrogeno",
    "Remisión",
    "Tipo Venta",
    "% BioEtanol",
    "% Éster metílico",
    "IDCCAA",
]
DB_FIELD_FUELS = {
    "Precio Gasoleo A": "gasoleo_a",
    "Precio Gasolina 95 E5": "gasolina_95",
    "Precio Gasolina 98 E5": "gasolina_98",
    "Precio Gases licuados del petróleo": "glp",
}


## Get from fp ##
def get_localities() -> dict:
    """Get the localities from the file."""
    return get_json_data(PATH_LOCALITIES)


def get_provinces() -> dict:
    """Get the provinces from the file."""
    return get_json_data(PATH_PROVINCES)


## Data fetching functions ##
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


## Data filtering functions ##
def _filter_station(station: dict, remove: list, rename: dict) -> dict:
    """Filter the station data to match the model.

    This function is called by update_db() and is not meant to be called directly.
    """

    for key in list(station.keys()):
        if key in remove:
            del station[key]
        elif key in rename:
            station[rename[key]] = station.pop(key)

    return station


## Create Locality and Province tables ##
def _create_complementary_tables() -> None:
    """
    Update the side tables (gas_locality and gas_province) with the data from the API.
    """

    print("[·] Updating complementary tables...")

    localities = get_localities()
    provinces = get_provinces()

    if Locality.objects.count() != len(localities):
        print("  [·] Updating localities...")
        Locality.objects.bulk_create(
            [
                Locality(id_mun=locality["IDMunicipio"], name=locality["Municipio"])
                for locality in localities
            ]
        )

    if Province.objects.count() != len(provinces):
        print("  [·] Updating provinces...")
        Province.objects.bulk_create(
            [
                Province(id_prov=province["IDPovincia"], name=province["Provincia"])
                for province in provinces  # Typo in the API data
            ]
        )

    print("[✓] Updated complementary tables.")
    print("---")


## Create Station table ##
def _update_stations(data: dict) -> None:
    """Update the stations in the database.

    This function is called by update_db() and is not meant to be called directly.

    It will create the stations that are not in the database, remove the ones that are
    not in the API and update the ones that are in both if needed.
    """

    print("[·] Updating stations...")
    stations = sorted(data["ListaEESSPrecio"], key=lambda x: int(x["IDEESS"]))

    # Create the stations that are not in the database
    stations_to_create: list[Station] = []
    stations_to_update: list[Station] = []

    len_stations = len(stations)
    now = timezone.now()
    for station in stations:
        print(f"  [·] {stations.index(station) + 1}/{len_stations}", end="")

        for key in list(station.keys()):
            if key in DB_FIELD_REMOVE or key in DB_FIELD_FUELS:
                del station[key]
            elif key in DB_FIELD_RENAME:
                station[DB_FIELD_RENAME[key]] = station.pop(key)

        station = _filter_station(
            station, DB_FIELD_REMOVE + list(DB_FIELD_FUELS), DB_FIELD_RENAME
        )

        locality = Locality.objects.filter(
            id_mun=int(station.pop("IDMunicipio"))
        ).first()
        province = Province.objects.filter(
            id_prov=int(station.pop("IDProvincia"))
        ).first()

        # Create the station
        db_stations = Station.objects.filter(id_eess=station["id_eess"])
        station_obj = Station(
            locality=locality, province=province, last_update=now, **station
        )

        if not db_stations.exists():
            stations_to_create.append(station_obj)
            print(" [C]", end="\r")
        else:
            stations_to_update.append(station_obj)
            print(" [U]", end="\r")

    print("  [·] Writing changes...", end="\r")

    Station.objects.bulk_create(stations_to_create)
    Station.objects.bulk_update(
        stations_to_update,
        fields=list(DB_FIELD_RENAME.values())[1:]
        + ["locality", "province", "last_update"],
    )
    print("[✓] Updated stations.   ")
    print("---")

    deleted_count, _ = Station.objects.exclude(
        id_eess__in=[station["id_eess"] for station in stations]
    ).delete()
    print(f"[✓] {deleted_count} old stations removed.")


## Create StationPrice table ##
def _update_prices(data: dict) -> None:
    """Update the prices in the database.

    This function is called by update_db() and is not meant to be called directly.

    It will add today's prices to the database.
    """

    stations = sorted(data["ListaEESSPrecio"], key=lambda x: int(x["IDEESS"]))
    prices = []

    print("[·] Updating prices...")
    len_stations = len(stations)
    today = date.today()
    for station in stations:
        print(f"  [·] {stations.index(station) + 1}/{len_stations}", end="\r")

        # Get the station
        station = _filter_station(
            station,
            DB_FIELD_REMOVE
            + list(DB_FIELD_RENAME.keys())[1:]
            + ["IDMunicipio", "IDProvincia"],
            {"IDEESS": "id_eess"},
        )
        db_station = Station.objects.get(id_eess=station["id_eess"])

        # Create the price
        for old_name, new_name in DB_FIELD_FUELS.items():
            station[new_name] = float(
                (value if (value := station.pop(old_name)) else "0").replace(",", ".")
            )
        station["id_eess"] = db_station
        station["date"] = today
        prices.append(StationPrice(**station))

    StationPrice.objects.bulk_create(prices)
    print("[✓] Updated prices.   ")
    print("---")


## Update database  ##
def update_db() -> None:
    """Download the data from the API to the database.

    This function will update the stations and prices in the database.

    Wrapper for _create_complementary_tables(), _update_stations() and _update_prices().
    """

    data = fetch_data()

    # Update localities and provinces
    _create_complementary_tables()

    # Update stations
    _update_stations(data)

    # Update prices
    if not StationPrice.objects.filter(date=date.today()).exists():
        _update_prices(data)

    print("[✓] All stations refreshed.")


## Purge stations ##
def purge_stations() -> None:
    """
    Remove all the stations from the database.
    """

    print("[·] Purging stations...", end="\r")
    Station.objects.all().delete()
    print("[✓] Purged stations.   ")
