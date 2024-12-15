# Appu Wrote These
# Copyright (C) 2023  Appuchia <appuchia@appu.ltd>

import json, lzma, os, requests
from datetime import date, datetime, timedelta
from decimal import Decimal
from multiprocessing import Pool
from tqdm import tqdm

from appuwrotethese.extras import (
    DATA_OLD_MINUTES,
    PATH_DATA,
    PATH_LOCALITIES,
    PATH_PROVINCES,
    get_json_data,
)
from gas.models import Locality, Province, Station, StationPrice

URL = "https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/"
HIST_URL = "https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestresHist/"
HIST_PATH_BASE = "gas/data/hist"
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
    """
    Get the latest data.

    If the file is older than `data_old_minutes` minutes, redownload it.
    """

    data_is_old = True

    if os.path.exists(path):
        try:
            with open(path, "r") as r:
                data = json.load(r)
        except json.JSONDecodeError:
            data = {}

        data_time = datetime.strptime(
            data.get("Fecha", "01/01/1970 00:00:00"), "%d/%m/%Y %H:%M:%S"
        )
        data_is_old = (datetime.now() - data_time) > timedelta(minutes=data_old_minutes)

    # Refresh the data
    if data_is_old:
        data = requests.get(URL).json()

        with open(path, "w") as f:
            json.dump(data, f)

    return data


## Create Locality and Province tables ##
def create_localities_provinces(
    localities_path=PATH_LOCALITIES, provinces_path=PATH_PROVINCES
) -> None:
    """Update the auxiliary tables `gas_locality` and `gas_province`"""

    localities = get_json_data(localities_path)
    provinces = get_json_data(provinces_path)

    if Locality.objects.count() != len(localities):
        Locality.objects.bulk_create(
            [Locality(id_mun=l["IDMunicipio"], name=l["Municipio"]) for l in localities]
        )

    if Province.objects.count() != len(provinces):
        Province.objects.bulk_create(
            [Province(id_prov=p["IDPovincia"], name=p["Provincia"]) for p in provinces]
        )


def create_station(data: dict, station: Station | None = None) -> Station:
    """Create a station from the data in `data`.

    If `station` is provided, it will update the station with the new data.
    """

    if not station:
        station = Station()
        station.id_eess = int(data["IDEESS"])

    station.company = data["Rótulo"]
    station.schedule = data["Horario"]
    station.address = data["Dirección"]
    station.latitude = data["Latitud"].replace(",", ".")
    station.longitude = data["Longitud (WGS84)"].replace(",", ".")
    station.locality = Locality.objects.get(id_mun=data["IDMunicipio"])
    station.province = Province.objects.get(id_prov=data["IDProvincia"])
    station.postal_code = int(data["C.P."])

    return station


def update_day_stations_prices(data: list, day: date, update: bool = False) -> None:
    """Update the database with stations and prices from `data`.

    Args
    ----
    `data` is a dict with the following structure:
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

    for price in tqdm(data, leave=False, desc=f"Processing {day}"):
        id_eess = int(price["IDEESS"])
        if id_eess not in stations:
            station = create_station(price)

            stations[station.id_eess] = station
            new_stations.add(station)

        elif update:  # Update station info if required
            station = stations[id_eess]
            station = create_station(price, station)

            updated_stations.add(station)

        if id_eess not in prices:
            prices.append(id_eess)
            new_prices.append(
                StationPrice(
                    station=stations.get(id_eess),
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
    days: int = 30, local_folder: str = "", workers: int = 1
) -> None:
    """Store historical prices in the database.

    If `local_folder` is provided, it will use all files in that folder.
    Otherwise, it will fetch the data from the API.
    """

    # Oldest date to process initially
    oldest = date.today() - timedelta(days=days)

    print(f"[·] Fetching {days} days using {workers} workers ({oldest} <-> ytd)")

    with Pool(processes=workers) as pool:
        for current_date in tqdm(
            (oldest + timedelta(days=i) for i in range(days)),
            leave=False,
            disable=(workers > 1),
        ):
            if StationPrice.objects.filter(date=current_date).exists():
                continue

            if local_folder:
                filename = local_folder + current_date.strftime("%Y-%m-%d.json.xz")
                if not os.path.isfile(filename):
                    continue

                with lzma.open(filename) as f:
                    data: list = json.load(f)["ListaEESSPrecio"]

                pool.apply_async(update_day_stations_prices, (data, current_date))
            else:
                pool.apply_async(get_data_and_update_day, (current_date,))

        pool.close()
        pool.join()

    print("---       ")
    print("[✓] Stored historical prices")
