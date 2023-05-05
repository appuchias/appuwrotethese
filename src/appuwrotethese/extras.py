# -------------------------------------
# This file includes all functions and
# info that is not included in the
# main files to keep things organized
# -------------------------------------

import json
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import OperationalError
from django.http.request import HttpRequest
from pathlib import Path
from typing import Any, Iterable, Callable


FILEPATH_ROOT = Path("./gas/")
PATH_PRODUCTS = FILEPATH_ROOT / "data" / "products.json"
PATH_LOCALITIES = FILEPATH_ROOT / "data" / "localities.json"
PATH_PROVINCES = FILEPATH_ROOT / "data" / "provinces.json"
PATH_DATA = FILEPATH_ROOT / "data" / "data.json"

# Minutes to consider data as old
DATA_OLD_MINUTES = 30


# BASH Colors
class BashColors:
    FG_LIGHTGRAY = "\033[37m"
    FG_DARKGRAY = "\033[37m"
    FAIL = "\033[91m"
    FG_RED = "\033[91m"
    FG_GREEN = "\033[92m"
    WARNING = "\033[93m"
    FG_YELLOW = "\033[93m"
    FG_BLUE = "\033[94m"
    FG_LIGHTMAGENTA = "\033[95m"
    FG_CYAN = "\033[96m"
    FG_WHITE = "\033[37m"
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    INVERTED = "\033[7m"
    HIDDEN = "\033[8m"


# First ocurrence that meets requirements
def firstof(
    iterable: Iterable, func: Callable[[Any], bool] | None = None, **kwargs
) -> Any:
    """Returns the first ocurrence of the iterable that meets the function,
    returning the default if none elements match.

    Sample usage: first([3, 6, 7], lambda x: x > 7, default=0) returns the first number
    strictly higher than 7 (0, the default, in this case)
    """

    it = filter(func, iterable)
    if "default" in kwargs:
        return next(it, kwargs[default])  # type: ignore - Ignore error
    return next(it)  # no default so raise `StopIteration`


# Take a dict and store it in a file
def store_json_data(data: dict, filepath: Path) -> None:
    """Store the JSON data in a file."""

    with open(filepath, "w") as w:
        json.dump(data, w, indent=4, ensure_ascii=True)


def get_json_data(filepath: Path) -> dict:
    """Get the JSON data from a file."""

    with open(filepath, "r") as r:
        data = json.load(r)

    return data


def get_user(request: HttpRequest):
    try:
        user = request.user.awtuser  # type: ignore
    except (OperationalError, ObjectDoesNotExist, AttributeError):
        # Error when user is not awtuser or it is not logged in
        user = request.user
        user.is_upgraded = True  # type: ignore

    return user
