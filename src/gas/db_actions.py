# Appu Wrote These
# Copyright (C) 2023  Appuchia <appuchia@appu.ltd>

import json, lzma, os, requests
from datetime import date, datetime, timedelta
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor

from appuwrotethese.extras import (
    DATA_OLD_MINUTES,
    PATH_DATA,
    PATH_LOCALITIES,
    PATH_PROVINCES,
    get_json_data,
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
    "Precio Gasoleo B": "price_gob",
    "Precio Gasolina 95 E5": "price_g95e5",
    "Precio Gasolina 95 E5 Premium": "price_g95e5_premium",
    "Precio Gasolina 95 E10": "price_g95e10",
    "Precio Gasolina 98 E5": "price_g98e5",
    "Precio Gasolina 98 E10": "price_g98e10",
    "Precio Gases licuados del petróleo": "price_glp",
    "Precio Gas Natural Comprimido": "price_gnc",
    "Precio Hidrogeno": "price_h2",
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

    localities = get_json_data(localities_path)
    provinces = get_json_data(provinces_path)

    if Locality.objects.count() != len(localities):
        Locality.objects.bulk_create(
            [
                Locality(id_mun=locality["IDMunicipio"], name=locality["Municipio"])
                for locality in localities
            ]
        )

    if Province.objects.count() != len(provinces):
        Province.objects.bulk_create(
            [  #                              v Typo exists in the API
                Province(id_prov=province["IDPovincia"], name=province["Provincia"])
                for province in provinces
            ]
        )


def update_day_stations_prices(data: list, day: date, update: bool = False) -> None:
    """Update the database with `prices_date`'s stations and prices

    Args
    ----
    `all_data` is a dict with the following structure:
    { 1999-12-31: [ { <station fields> }, <more stations> ], <more dates> }

    If `update` is True, it will update existing stations and prices, even if
    they have the same date.

    Returns
    -------
    2 tuples with the number of added stations and prices and the number
    of updated stations and prices, respectively.
    """
    ids_eess = (int(station["IDEESS"]) for station in data)

    stations = Station.objects.in_bulk(ids_eess, field_name="id_eess")
    prices = [price.station.id_eess for price in StationPrice.objects.filter(date=day)]

    new_stations = set()
    new_prices = list()

    updated_stations = set()
    updated_prices = list()

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

        elif update:  # Update station info if required
            station = stations[id_eess]
            station.company = price["Rótulo"]
            station.schedule = price["Horario"]
            station.address = price["Dirección"]
            station.latitude = price["Latitud"].replace(",", ".")
            station.longitude = price["Longitud (WGS84)"].replace(",", ".")
            station.locality = Locality.objects.get(id_mun=price["IDMunicipio"])
            station.province = Province.objects.get(id_prov=price["IDProvincia"])
            station.postal_code = int(price["C.P."])

            updated_stations.add(station)

        if not id_eess in prices:
            prices.append(id_eess)
            new_prices.append(
                StationPrice(
                    station=stations.get(id_eess, None),
                    date=day,
                    **{
                        DB_FIELD_FUELS[key]: Decimal(price[key].replace(",", "."))
                        for key in DB_FIELD_FUELS
                        if price[key]
                    },
                )
            )
        elif update:
            updated_prices.append(
                StationPrice.objects.get(station=stations[id_eess], date=day)
            )
            for key in DB_FIELD_FUELS:  # Update fuel prices individually
                setattr(
                    updated_prices[-1],
                    DB_FIELD_FUELS[key],
                    Decimal(price[key].replace(",", ".")) if price[key] else None,
                )

    if update:  # Update required stations and prices
        if updated_stations:
            Station.objects.bulk_update(
                updated_stations,
                fields=[
                    "company",
                    "schedule",
                    "address",
                    "latitude",
                    "longitude",
                    "locality",
                    "province",
                    "postal_code",
                ],
            )
        if updated_prices:
            StationPrice.objects.bulk_update(
                updated_prices, fields=list(DB_FIELD_FUELS.values())
            )

    Station.objects.bulk_create(new_stations)
    StationPrice.objects.bulk_create(new_prices)

    print(day, end="\r")


def get_data_and_update_day(current_date: date) -> None:
    """Get the data for `current_date` and update the database.

    If the data is already in the database, it will not be updated.
    """

    if StationPrice.objects.filter(date=current_date).exists():
        return

    update_day_stations_prices(
        requests.get(HIST_URL + current_date.strftime("%d-%m-%Y")).json()[
            "ListaEESSPrecio"
        ],
        current_date,
    )


## Store historical prices ##
def store_historical_prices(
    days: int = 30, local_folder: str = "", threads: int = 1
) -> None:
    """Store historical prices in the database.

    If `local_folder` is provided, it will use all files in that folder.
    Otherwise, it will store the data from the last year.
    """

    print(f"[·] Fetching prices from the last {days} days ({threads} threads)")

    today = date.today()
    current_date = today - timedelta(days=days)

    with ThreadPoolExecutor(max_workers=threads) as executor:
        while current_date <= today:
            if StationPrice.objects.filter(date=current_date).exists():
                current_date += timedelta(days=1)
                continue

            if local_folder:
                filename = local_folder + current_date.strftime("%Y-%m-%d.json.xz")
                if not os.path.isfile(filename):
                    current_date += timedelta(days=1)
                    continue

                with lzma.open(filename) as f:
                    data: list = json.load(f)["ListaEESSPrecio"]

                executor.submit(update_day_stations_prices, data, current_date)
            else:
                executor.submit(get_data_and_update_day, current_date)

            # print(current_date, end="\r")
            current_date += timedelta(days=1)

    # print("---       ")
    print("[✓] Stored historical prices")
