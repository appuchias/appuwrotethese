# Appu Wrote These
# Copyright (C) 2023  Appuchia <appuchia@appu.ltd>

from datetime import date
from typing import Iterable

from gas.models import StationPrice


def format_prices(prices: Iterable[StationPrice], fuel_abbr: str, q_date: date) -> dict:
    fuels = ["GOA", "G95E5", "G98E5", "GLP"]

    return {
        "fuel_type": fuel_abbr,
        "date": q_date,
        "prices": {
            price.station.id_eess: {
                f"price_{fuel.lower()}": getattr(price, f"price_{fuel.lower()}")
                for fuel in fuels
            }
            for price in prices
        },
    }
