import settings as cfg

from hex_grid import (
    is_hex_on_map,
)

from map_data import (
    load_default_map_data,
    save_default_map_data,
)


# --------------------------------------------------
# MAP EDITOR BRUSH NAMES
# --------------------------------------------------

BRUSH_WALL = "wall"

BRUSH_MUD = "mud"

BRUSH_WATER_SHALLOW = (
    "water_shallow"
)

BRUSH_WATER_DEEP = (
    "water_deep"
)

BRUSH_WATER_VERY_DEEP = (
    "water_very_deep"
)

BRUSH_ERASER = "eraser"

BRUSH_PLAYER_START = (
    "player_start"
)


# --------------------------------------------------
# MAP STATE
# --------------------------------------------------

class MapState:

    def __init__(
        self,
    ):

        self.load_data(
            load_default_map_data()
        )


    # --------------------------------------------------
    # LOAD MAP DATA INTO CURRENT SESSION
    # --------------------------------------------------

    def load_data(
        self,
        data,
    ):

        self.player_start = tuple(
            data[
                "player_start"
            ]
        )


        self.wall_hexes = set(
            data[
                "walls"
            ]
        )


        self.mud_hexes = set(
            data[
                "mud"
            ]
        )


        self.water_shallow_hexes = set(
            data[
                "water_shallow"
            ]
        )


        self.water_deep_hexes = set(
            data[
                "water_deep"
            ]
        )


        self.water_very_deep_hexes = set(
            data[
                "water_very_deep"
            ]
        )


    # --------------------------------------------------
    # CURRENT MAP -> SAVEABLE DATA
    # --------------------------------------------------

    def to_data(
        self,
    ):

        return {
            "player_start": (
                self.player_start
            ),

            "walls": set(
                self.wall_hexes
            ),

            "mud": set(
                self.mud_hexes
            ),

            "water_shallow": set(
                self.water_shallow_hexes
            ),

            "water_deep": set(
                self.water_deep_hexes
            ),

            "water_very_deep": set(
                self.water_very_deep_hexes
            ),
        }


    # --------------------------------------------------
    # ERASE TERRAIN AT ONE HEX
    # --------------------------------------------------

    def clear_terrain_at(
        self,
        hex_position,
    ):

        self.wall_hexes.discard(
            hex_position
        )

        self.mud_hexes.discard(
            hex_position
        )

        self.water_shallow_hexes.discard(
            hex_position
        )

        self.water_deep_hexes.discard(
            hex_position
        )

        self.water_very_deep_hexes.discard(
            hex_position
        )


    # --------------------------------------------------
    # MAP EDITOR PAINT
    # --------------------------------------------------

    def paint_hex(
        self,
        hex_position,
        brush,
    ):

        if not is_hex_on_map(
            hex_position
        ):

            return (
                False,
                "Outside map.",
            )


        # --------------------------------------------------
        # PLAYER START BRUSH
        # --------------------------------------------------

        if brush == BRUSH_PLAYER_START:

            if (
                hex_position
                in self.wall_hexes
            ):

                return (
                    False,
                    "Player start cannot be inside a wall.",
                )


            self.player_start = (
                hex_position
            )


            return (
                True,
                (
                    "Player start set to "
                    f"{hex_position}."
                ),
            )


        # --------------------------------------------------
        # ERASER
        # --------------------------------------------------

        if brush == BRUSH_ERASER:

            self.clear_terrain_at(
                hex_position
            )


            return (
                True,
                "Terrain erased.",
            )


        # --------------------------------------------------
        # PREVENT WALL OVER PLAYER START
        # --------------------------------------------------

        if (
            brush == BRUSH_WALL
            and
            hex_position
            == self.player_start
        ):

            return (
                False,
                "Cannot paint wall over player start.",
            )


        # Only one terrain material may occupy a cell.

        self.clear_terrain_at(
            hex_position
        )


        # --------------------------------------------------
        # WALL
        # --------------------------------------------------

        if brush == BRUSH_WALL:

            self.wall_hexes.add(
                hex_position
            )


        # --------------------------------------------------
        # MUD
        # --------------------------------------------------

        elif brush == BRUSH_MUD:

            self.mud_hexes.add(
                hex_position
            )


        # --------------------------------------------------
        # SHALLOW WATER
        # --------------------------------------------------

        elif (
            brush
            == BRUSH_WATER_SHALLOW
        ):

            self.water_shallow_hexes.add(
                hex_position
            )


        # --------------------------------------------------
        # DEEP WATER
        # --------------------------------------------------

        elif (
            brush
            == BRUSH_WATER_DEEP
        ):

            self.water_deep_hexes.add(
                hex_position
            )


        # --------------------------------------------------
        # VERY DEEP WATER
        # --------------------------------------------------

        elif (
            brush
            == BRUSH_WATER_VERY_DEEP
        ):

            self.water_very_deep_hexes.add(
                hex_position
            )


        else:

            return (
                False,
                "Unknown editor brush.",
            )


        return (
            True,
            (
                "Painted "
                f"{brush.replace('_', ' ')}."
            ),
        )


    # --------------------------------------------------
    # WEIGHTED TERRAIN COST TABLE
    # --------------------------------------------------

    def get_terrain_move_costs(
        self,
    ):

        costs = {}


        costs.update(
            {
                hex_position:
                cfg.MUD_MOVE_COST

                for hex_position
                in self.mud_hexes
            }
        )


        costs.update(
            {
                hex_position:
                cfg.WATER_SHALLOW_MOVE_COST

                for hex_position
                in self.water_shallow_hexes
            }
        )


        costs.update(
            {
                hex_position:
                cfg.WATER_DEEP_MOVE_COST

                for hex_position
                in self.water_deep_hexes
            }
        )


        costs.update(
            {
                hex_position:
                cfg.WATER_VERY_DEEP_MOVE_COST

                for hex_position
                in self.water_very_deep_hexes
            }
        )


        return costs


    # --------------------------------------------------
    # SAVE CURRENT MAP AS PERMANENT DEFAULT
    # --------------------------------------------------

    def save_as_default(
        self,
    ):

        return save_default_map_data(
            self.to_data()
        )