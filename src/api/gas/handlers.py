# Appu Wrote These
# Copyright (C) 2023  Appuchia <appuchia@appu.ltd>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
