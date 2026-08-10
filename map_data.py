import json

from pathlib import Path

import settings as cfg

from hex_grid import (
    offset_to_axial,
)


# --------------------------------------------------
# DEFAULT MAP FILE
# --------------------------------------------------

DEFAULT_MAP_PATH = (
    Path(__file__).resolve().parent
    / "maps"
    / "default_map.json"
)


# --------------------------------------------------
# RECTANGULAR OFFSET MAP HELPER
# --------------------------------------------------

def _rect_hexes(
    column_start,
    column_end,
    row_start,
    row_end,
):

    return {
        offset_to_axial(
            column,
            row,
        )
        for column in range(
            column_start,
            column_end,
        )
        for row in range(
            row_start,
            row_end,
        )
    }


# --------------------------------------------------
# BUILT-IN WALL
# --------------------------------------------------

BUILTIN_WALL_HEXES = (
    _rect_hexes(
        13,
        15,
        5,
        15,
    )
)


# --------------------------------------------------
# BUILT-IN MUD TEST AREA
# --------------------------------------------------

BUILTIN_MUD_HEXES = (
    _rect_hexes(
        19,
        24,
        8,
        13,
    )
)


# --------------------------------------------------
# BUILT-IN WATER TEST AREA
# --------------------------------------------------

_water_all = (
    _rect_hexes(
        20,
        25,
        2,
        7,
    )
)


_water_deep_or_more = (
    _rect_hexes(
        21,
        24,
        3,
        6,
    )
)


BUILTIN_WATER_VERY_DEEP_HEXES = {
    offset_to_axial(
        22,
        4,
    )
}


BUILTIN_WATER_DEEP_HEXES = (
    _water_deep_or_more
    - BUILTIN_WATER_VERY_DEEP_HEXES
)


BUILTIN_WATER_SHALLOW_HEXES = (
    _water_all
    - _water_deep_or_more
)


# --------------------------------------------------
# JSON HELPERS
# --------------------------------------------------

def _hexes_from_json(
    values,
):

    return {
        tuple(
            value
        )
        for value in values
    }


def _sorted_hexes(
    values,
):

    return [
        list(
            value
        )
        for value in sorted(
            values
        )
    ]


# --------------------------------------------------
# BUILT-IN FALLBACK MAP
# --------------------------------------------------

def built_in_map_data():

    return {
        "player_start": tuple(
            cfg.PLAYER_START
        ),

        "walls": set(
            BUILTIN_WALL_HEXES
        ),

        "mud": set(
            BUILTIN_MUD_HEXES
        ),

        "water_shallow": set(
            BUILTIN_WATER_SHALLOW_HEXES
        ),

        "water_deep": set(
            BUILTIN_WATER_DEEP_HEXES
        ),

        "water_very_deep": set(
            BUILTIN_WATER_VERY_DEEP_HEXES
        ),
    }


# --------------------------------------------------
# LOAD DEFAULT MAP
# --------------------------------------------------

def load_default_map_data():

    # No saved editor map yet.
    #
    # Use the built-in Python starter map.

    if not DEFAULT_MAP_PATH.exists():

        return built_in_map_data()


    with DEFAULT_MAP_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:

        raw = json.load(
            file
        )


    return {
        "player_start": tuple(
            raw.get(
                "player_start",
                cfg.PLAYER_START,
            )
        ),

        "walls": _hexes_from_json(
            raw.get(
                "walls",
                [],
            )
        ),

        "mud": _hexes_from_json(
            raw.get(
                "mud",
                [],
            )
        ),

        "water_shallow": _hexes_from_json(
            raw.get(
                "water_shallow",
                [],
            )
        ),

        "water_deep": _hexes_from_json(
            raw.get(
                "water_deep",
                [],
            )
        ),

        "water_very_deep": _hexes_from_json(
            raw.get(
                "water_very_deep",
                [],
            )
        ),
    }


# --------------------------------------------------
# SAVE CURRENT MAP AS DEFAULT
# --------------------------------------------------

def save_default_map_data(
    data,
):

    DEFAULT_MAP_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )


    raw = {
        "player_start": list(
            data[
                "player_start"
            ]
        ),

        "walls": _sorted_hexes(
            data[
                "walls"
            ]
        ),

        "mud": _sorted_hexes(
            data[
                "mud"
            ]
        ),

        "water_shallow": _sorted_hexes(
            data[
                "water_shallow"
            ]
        ),

        "water_deep": _sorted_hexes(
            data[
                "water_deep"
            ]
        ),

        "water_very_deep": _sorted_hexes(
            data[
                "water_very_deep"
            ]
        ),
    }


    with DEFAULT_MAP_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            raw,
            file,
            indent=4,
        )


    return DEFAULT_MAP_PATH