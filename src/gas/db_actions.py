# Appu Wrote These
# Copyright (C) 2023  Appuchia <appuchia@appu.ltd>

import json, lzma, os, requests, time
from datetime import date, datetime, timedelta
from decimal import Decimal

from appuwrotethese.extras import (
    DATA_OLD_MINUTES,
    PATH_DATA,
    PATH_LOCALITIES,
    PATH_PROVINCES,
    get_json_data,
    ShellCodes as C,
)
from gas.models import Locality, Province, Station, StationPrice

HIST_URL = "https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestresHist/"
HIST_PATH_BASE = "gas/data/hist"
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
    "Precio Gasolina 95 E5": "price_g95e5",
    "Precio Gasolina 98 E5": "price_g98e5",
    "Precio Gases licuados del petróleo": "price_glp",
}


## Data fetching functions ##
def get_data(path=PATH_DATA, data_old_minutes=DATA_OLD_MINUTES) -> dict:
    """Get the latest data.

    If the file is older than `data_old_minutes` minutes, redownload it.
    """

    # Try to use the data in the file
    try:
        with open(path, "r") as r:
            data = json.load(r)
    except FileNotFoundError:
        data = {}  # Simulate the data is old

    # Determine if the data is old
    try:
        date = data["Fecha"]
    except KeyError:
        data_is_old = True
    else:
        data_time = datetime.strptime(date, "%d/%m/%Y %H:%M:%S")
        # True if data is older than DATA_OLD_MINUTES minutes
        data_is_old = datetime.now() - data_time > timedelta(minutes=data_old_minutes)

    # Refresh the data
    if data_is_old:
        data = requests.get(
            "https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/"
        ).json()

        with open(path, "w") as f:
            json.dump(data, f, indent=4)

    return data


## Create Locality and Province tables ##
def create_localities_provinces(
    localities_path=PATH_LOCALITIES, provinces_path=PATH_PROVINCES
) -> None:
    """Update the aux tables (gas_locality and gas_province)."""

    # print("[·] Updating complementary tables...")

    localities = get_json_data(localities_path)
    provinces = get_json_data(provinces_path)

    if Locality.objects.count() != len(localities):
        # print("  [·] Updating localities...")
        Locality.objects.bulk_create(
            [
                Locality(id_mun=locality["IDMunicipio"], name=locality["Municipio"])
                for locality in localities
            ]
        )

    if Province.objects.count() != len(provinces):
        # print("  [·] Updating provinces...")
        Province.objects.bulk_create(
            [  # Typo exists in the API
                Province(id_prov=province["IDPovincia"], name=province["Provincia"])
                for province in provinces
            ]
        )

    # print("[✓] Updated complementary tables.")
    # print("---")


## Update Station and StationPrice tables ##
def update_station_prices(data: list, prices_date: date = date.today()) -> None:
    """Update the database with `prices_date`'s stations and prices"""

    id_eess = (int(station["IDEESS"]) for station in data)

    stations = Station.objects.in_bulk(id_eess, field_name="id_eess")
    prices = [
        price.station.id_eess for price in StationPrice.objects.filter(date=prices_date)
    ]

    new_prices = list()
    new_stations = set()
    for price in data:
        id_eess = int(price["IDEESS"])
        if not id_eess in stations:
            station = Station(
                id_eess=id_eess,
                company=price["Rótulo"],
                schedule=price["Horario"],
                address=price["Dirección"],
                latitude=price["Latitud"].replace(",", "."),
                longitude=price["Longitud (WGS84)"].replace(",", "."),
                locality=Locality.objects.get(id_mun=price["IDMunicipio"]),
                province=Province.objects.get(id_prov=price["IDProvincia"]),
                postal_code=int(price["C.P."]),
            )

            stations[station.id_eess] = station
            new_stations.add(station)

        if not id_eess in prices:
            prices.append(id_eess)
            new_prices.append(
                StationPrice(
                    station=stations.get(id_eess, None),
                    date=prices_date,
                    **{
                        DB_FIELD_FUELS[key]: Decimal(price[key].replace(",", "."))
                        if price[key]
                        else None
                        for key in DB_FIELD_FUELS
                    },
                )
            )

    Station.objects.bulk_create(new_stations)
    StationPrice.objects.bulk_create(new_prices)

    # print("[✓] Updated prices.     ")
    # print("---")


## Store historical prices ##
def store_historical_prices(days: int = 365, local_folder: str = "") -> None:
    """Store historical prices in the database.

    If `local_folder` is provided, it will use all files in that folder.
    Otherwise, it will store the data from the last year.
    """

    print("[·] Storing historical prices")
    lines = 2
    print("\n" * (lines - 1))

    today = date.today()
    current_date = today - timedelta(days=days)
    days_left = (today - current_date).days

    while current_date <= today:
        start = time.perf_counter()

        print(
            f"{C.up(lines)} [·] Populating {current_date}. {days_left} days left{C.CLR}"
        )
        if StationPrice.objects.filter(date=current_date).exists():
            print("\n" * (lines - 2))
            current_date += timedelta(days=1)
            days_left -= 1
            continue

        if local_folder:
            filename = local_folder + current_date.strftime("%Y-%m-%d.json.xz")
            if not os.path.isfile(filename):
                print("\n" * (lines - 2))
                current_date += timedelta(days=1)
                days_left -= 1
                continue

            with lzma.open(filename) as f:
                data: list = json.load(f)["ListaEESSPrecio"]
        else:
            data: list = requests.get(
                HIST_URL + current_date.strftime("%d-%m-%Y")
            ).json()["ListaEESSPrecio"]

        elapsed_query = time.perf_counter() - start
        update_station_prices(data, prices_date=current_date)
        elapsed_total = time.perf_counter() - start

        eta = elapsed_total * days_left
        eta_h = int(eta // 3600)
        eta_m = int((eta % 3600) // 60)

        print(
            f"     Last:{elapsed_total:.2f}s [Query:{elapsed_query:.2f}s, DB:{elapsed_total - elapsed_query:.2f}s] ETA {eta_h}h{eta_m:02}min{C.CLR}"
        )
        current_date += timedelta(days=1)
        days_left -= 1

    print(f"{C.up(lines + 1)}[✓] Stored historical prices{C.CLR}")
    print(f"---{C.CLR}")
    print(f"{C.CLR}\n" * (lines - 1), end="")
