import math

import settings as cfg


# --------------------------------------------------
# HEX DIRECTIONS
# --------------------------------------------------

HEX_DIRECTIONS = (
    (1, 0),
    (1, -1),
    (0, -1),
    (-1, 0),
    (-1, 1),
    (0, 1),
)


# These are the same six neighbours, but ordered
# to match the six polygon edges created by
# hex_corners().

HEX_EDGE_NEIGHBORS = (
    (1, 0),
    (0, 1),
    (-1, 1),
    (-1, 0),
    (0, -1),
    (1, -1),
)


# --------------------------------------------------
# HEX NEIGHBOURS
# --------------------------------------------------

def get_neighbors(hex_position):
    q, r = hex_position

    neighbors = []

    for dq, dr in HEX_DIRECTIONS:
        neighbor = (
            q + dq,
            r + dr,
        )

        neighbors.append(
            neighbor
        )

    return neighbors


# --------------------------------------------------
# HEX DISTANCE
# --------------------------------------------------

def hex_distance(hex_a, hex_b):
    q1, r1 = hex_a
    q2, r2 = hex_b

    dq = (
        q2 - q1
    )

    dr = (
        r2 - r1
    )

    return max(
        abs(dq),
        abs(dr),
        abs(dq + dr),
    )


# --------------------------------------------------
# HEX RANGE
# --------------------------------------------------

def hexes_within_range(
    center,
    max_distance,
):
    center_q, center_r = center

    reachable = set()

    for dq in range(
        -max_distance,
        max_distance + 1,
    ):

        minimum_dr = max(
            -max_distance,
            -dq - max_distance,
        )

        maximum_dr = min(
            max_distance,
            -dq + max_distance,
        )

        for dr in range(
            minimum_dr,
            maximum_dr + 1,
        ):

            hex_position = (
                center_q + dq,
                center_r + dr,
            )

            reachable.add(
                hex_position
            )

    return reachable


# --------------------------------------------------
# AXIAL ROUNDING
# --------------------------------------------------

def axial_round(
    q_float,
    r_float,
):
    x = q_float
    z = r_float

    y = (
        -x
        - z
    )

    rounded_x = round(
        x
    )

    rounded_y = round(
        y
    )

    rounded_z = round(
        z
    )

    x_difference = abs(
        rounded_x - x
    )

    y_difference = abs(
        rounded_y - y
    )

    z_difference = abs(
        rounded_z - z
    )

    if (
        x_difference > y_difference
        and
        x_difference > z_difference
    ):
        rounded_x = (
            -rounded_y
            - rounded_z
        )

    elif (
        y_difference
        > z_difference
    ):
        rounded_y = (
            -rounded_x
            - rounded_z
        )

    else:
        rounded_z = (
            -rounded_x
            - rounded_y
        )

    return (
        int(rounded_x),
        int(rounded_z),
    )


# --------------------------------------------------
# OFFSET TO AXIAL
# --------------------------------------------------

def offset_to_axial(
    column,
    row,
):
    q = column

    r = (
        row
        - (
            column
            - (column & 1)
        ) // 2
    )

    return (
        q,
        r,
    )


# --------------------------------------------------
# AXIAL TO OFFSET
# --------------------------------------------------

def axial_to_offset(
    hex_position
):
    q, r = hex_position

    column = q

    row = (
        r
        + (
            q
            - (q & 1)
        ) // 2
    )

    return (
        column,
        row,
    )


# --------------------------------------------------
# MAP BOUNDARY CHECK
# --------------------------------------------------

def is_hex_on_map(
    hex_position
):
    column, row = axial_to_offset(
        hex_position
    )

    return (
        0
        <= column
        < cfg.GRID_COLUMNS
        and
        0
        <= row
        < cfg.GRID_ROWS
    )


# --------------------------------------------------
# AXIAL TO SCREEN PIXELS
# --------------------------------------------------

def axial_to_pixel(
    hex_position
):
    q, r = hex_position

    x = (
        cfg.HEX_SIZE
        * 1.5
        * q
    )

    y = (
        cfg.HEX_SIZE
        * math.sqrt(3)
        * (
            r
            + q / 2
        )
    )

    return (
        x + cfg.GRID_ORIGIN_X,
        y + cfg.GRID_ORIGIN_Y,
    )


# --------------------------------------------------
# SCREEN PIXELS TO AXIAL
# --------------------------------------------------

def pixel_to_axial(
    pixel_position
):
    pixel_x, pixel_y = (
        pixel_position
    )

    local_x = (
        pixel_x
        - cfg.GRID_ORIGIN_X
    )

    local_y = (
        pixel_y
        - cfg.GRID_ORIGIN_Y
    )

    q_float = (
        (
            2 / 3
        )
        * local_x
        / cfg.HEX_SIZE
    )

    r_float = (
        (
            -1 / 3
        )
        * local_x
        / cfg.HEX_SIZE
        +
        (
            math.sqrt(3) / 3
        )
        * local_y
        / cfg.HEX_SIZE
    )

    return axial_round(
        q_float,
        r_float,
    )


# --------------------------------------------------
# HEX POLYGON CORNERS
# --------------------------------------------------

def hex_corners(
    center,
    size=None,
):
    center_x, center_y = center

    if size is None:
        size = cfg.HEX_SIZE

    points = []

    for corner in range(6):

        angle_degrees = (
            60 * corner
        )

        angle_radians = math.radians(
            angle_degrees
        )

        point_x = (
            center_x
            + size
            * math.cos(
                angle_radians
            )
        )

        point_y = (
            center_y
            + size
            * math.sin(
                angle_radians
            )
        )

        points.append(
            (
                point_x,
                point_y,
            )
        )

    return points