import json, requests
from datetime import date, datetime
from decimal import Decimal
import django.utils.timezone as timezone

from appuwrotethese.extras import (
    DATA_OLD_MINUTES,
    PATH_DATA,
    PATH_LOCALITIES,
    PATH_PROVINCES,
    get_json_data,
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
DB_FIELD_FUELS = {
    "Precio Gasoleo A": "price_goa",
    "Precio Gasolina 95 E5": "price_g95",
    "Precio Gasolina 98 E5": "price_g98",
    "Precio Gases licuados del petróleo": "price_glp",
}


## Data fetching functions ##
def get_data() -> dict:
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


## Create Locality and Province tables ##
def _create_complementary_tables() -> None:
    """Update the aux tables (gas_locality and gas_province)."""

    print("[·] Updating complementary tables...")

    localities = get_json_data(PATH_LOCALITIES)
    provinces = get_json_data(PATH_PROVINCES)

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
def _update_stations(stations: list) -> None:
    """Update the stations in the database.

    This function is called by update_db() and is not meant to be called directly.

    It will create the stations that are not in the database, remove the ones that are
    not in the API and update the ones that are in both if needed.
    """

    print("[·] Updating stations...")

    if Station.objects.count() == len(stations):
        print("[✓] Stations are up to date.")
        print("---")
        return

    # Create the stations that are not in the database
    stations_to_create: list[Station] = []
    # stations_to_update: list[Station] = []

    len_stations = len(stations)
    now = timezone.now()
    for idx, station in enumerate(stations):
        print(f"  [·] {idx + 1}/{len_stations}", end="\r")

        locality = Locality.objects.filter(
            id_mun=int(station.pop("IDMunicipio"))
        ).first()
        province = Province.objects.filter(
            id_prov=int(station.pop("IDProvincia"))
        ).first()

        # Create the station
        new_station = Station(
            locality=locality,
            province=province,
            last_update=now,
            **{
                DB_FIELD_RENAME[key]: value
                for key, value in station.items()
                if key in DB_FIELD_RENAME
            },
        )
        db_stations = Station.objects.filter(id_eess=station["IDEESS"])

        if not db_stations.exists():
            stations_to_create.append(new_station)
            # print(" [C]", end="\r")
        # elif db_stations.first() != station_obj:
        #     stations_to_update.append(station_obj)
        #     print(" [U]", end="\r")

    print("  [·] Writing changes...", end="\r")
    print(f"  [·] Creating {len(stations_to_create)} stations...")
    Station.objects.bulk_create(stations_to_create)
    # print(f"  [·] Updating {len(stations_to_update)} stations...")
    # Station.objects.bulk_update(
    #     stations_to_update,
    #     fields=list(DB_FIELD_RENAME.values())[1:]
    #     + ["locality", "province", "last_update"],
    # )
    print("[✓] Updated stations.   ")
    print("---")


## Create StationPrice table ##
def _update_prices(stations: list) -> None:
    """Update the prices in the database.

    This function is called by update_db() and is not meant to be called directly.

    It will add today's prices to the database.
    """

    prices_to_create: list[StationPrice] = []
    prices_to_update: list[StationPrice] = []

    print("[·] Updating prices...")
    len_stations = len(stations)
    for idx, station in enumerate(stations):
        print(f"  [·] {idx + 1}/{len_stations}", end="\r")

        new_price = StationPrice(
            station=Station.objects.get(id_eess=station.get("IDEESS")),
            date=date.today(),
            **{
                DB_FIELD_FUELS[key]: Decimal(value.replace(",", ".")) if value else None
                for key, value in station.items()
                if key in DB_FIELD_FUELS
            },
        )

        # Create or update the price
        db_price = StationPrice.objects.filter(
            station=new_price.station, date=new_price.date
        ).first()
        if not db_price:
            prices_to_create.append(new_price)
        elif db_price != new_price:
            new_price.id = db_price.id  # PK needed for bulk_update  # type: ignore
            prices_to_update.append(db_price)

    print("  [·] Writing changes...", end="\r")
    print(f"  [·] {len(prices_to_create)} prices to create.")
    StationPrice.objects.bulk_create(prices_to_create)
    print(f"  [·] {len(prices_to_update)} prices to update.")
    StationPrice.objects.bulk_update(
        prices_to_update,
        fields=list(DB_FIELD_FUELS.values()),
    )

    print("[✓] Updated prices.     ")
    print("---")


## Update database  ##
def update_db() -> None:
    """Download the data from the API to the database.

    This function will update the stations and prices in the database.

    Wrapper for _create_complementary_tables(), _update_stations() and _update_prices().
    """

    # Update localities and provinces
    _create_complementary_tables()

    # Update stations
    _update_stations(get_data()["ListaEESSPrecio"])

    # Update prices
    _update_prices(get_data()["ListaEESSPrecio"])

    print("[✓] All stations refreshed.")


## Purge stations ##
def purge_stations() -> None:
    """Remove all the stations from the database."""

    print("[·] Purging stations...", end="\r")
    Station.objects.all().delete()
    print("[✓] Purged stations.   ")


## Purge prices ##
def purge_prices() -> None:
    """Remove all the prices from the database."""

    print("[·] Purging prices...", end="\r")
    StationPrice.objects.all().delete()
    print("[✓] Purged prices.   ")

