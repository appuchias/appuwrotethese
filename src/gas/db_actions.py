from datetime import datetime
import json, requests

from appuwrotethese.extras import (
    get_json_data,
    DATA_OLD_MINUTES,
    PATH_DATA,
    PATH_LOCALITIES,
    PATH_PROVINCES,
)
from gas.models import Locality, Province, Station

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


## Update database  ##
def update_db() -> None:
    """
    Load the data from the API into the database.
    """

    stations = sorted(fetch_data()["ListaEESSPrecio"], key=lambda x: int(x["IDEESS"]))
    stations_len = len(stations)

    # Update localities and provinces
    _create_complementary_tables()

    # Change station fields to match the database
    stations_to_create: list[Station] = []
    stations_to_update: list[Station] = []

    for idx, station in enumerate(stations):
        # Modify or remove fields
        for key in list(station.keys()):
            if key in DB_FIELD_RENAME:
                station[DB_FIELD_RENAME[key]] = station.pop(key)
            elif key in DB_FIELD_REMOVE:
                del station[key]

        for old_name, new_name in DB_FIELD_FUELS.items():
            station[new_name] = float(
                (station[old_name] if station[old_name] else "0").replace(",", ".")
            )

        # Add the complementary fields
        print(
            f"  [·] Clasifying station {idx}/{stations_len}",
            end=" ",
        )
        locality = Locality.objects.filter(
            id_mun=int(station.pop("IDMunicipio"))
        ).first()
        province = Province.objects.filter(
            id_prov=int(station.pop("IDProvincia"))
        ).first()

        # Determine if the station has to be created or updated
        station_new = Station(locality=locality, province=province, **station)
        station_obj = Station.objects.filter(id_eess=station["id_eess"])
        if not station_obj:
            stations_to_create.append(station_new)
            print(" [C]", end="\r")
        elif station_new != station_obj.first():
            stations_to_update.append(station_new)
            print(" [U]", end="\r")

    print("[✓] Clasified stations." + " " * 20)
    print(f"    {len(stations_to_create)} stations to create.")
    print(f"    {len(stations_to_update)} stations to update.")

    # Create the stations
    if len(stations_to_create) > 0:
        print("[·] Creating stations...", end="\r")
        Station.objects.bulk_create(stations_to_create)
        print("[✓] Created stations.   ")

    # Update the stations
    if len(stations_to_update) > 0:
        print("[·] Updating stations...", end="\r")
        Station.objects.bulk_update(
            stations_to_update,
            list(DB_FIELD_RENAME.values())[1:]  # Remove id_eess
            + ["locality", "province"],  # Add locality and province
        )
        print("[✓] Updated stations.")

    print("---\n[✓] All stations refreshed.")


## Purge stations ##
def purge_stations() -> None:
    """
    Remove all the stations from the database.
    """

    print("[·] Purging stations...", end="\r")
    Station.objects.all().delete()
    print("[✓] Purged stations.   ")
