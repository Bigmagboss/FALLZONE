from hex_grid import offset_to_axial


# --------------------------------------------------
# FALLZONE STATIC MAP DATA
# --------------------------------------------------

# The wall is described using visible map
# column/row positions because that is much easier
# to understand when designing a level.
#
# We then convert those positions into axial
# coordinates used by the game logic.


# --------------------------------------------------
# TEST WALL
# --------------------------------------------------

WALL_COLUMNS = (
    13,
    14,
)


WALL_ROW_START = 5

WALL_ROW_END = 15


WALL_HEXES = {
    offset_to_axial(
        column,
        row,
    )
    for column in WALL_COLUMNS
    for row in range(
        WALL_ROW_START,
        WALL_ROW_END,
    )
}