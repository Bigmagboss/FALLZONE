import math

import settings as cfg

HEX_DIRECTIONS = (
    (1, 0),
    (1, -1),
    (0, -1),
    (-1, 0),
    (-1, 1),
    (0, 1),
)

HEX_EDGE_NEIGHBORS = (
    (1, 0),
    (0, 1),
    (-1, 1),
    (-1, 0),
    (0, -1),
    (1, -1),
)

def get_neighbors(hex_position):
    q, r = hex_position

    neighbors = []

    for dq, dr in HEX_DIRECTIONS:
        neighbor = (
            q + dq,
            r + dr,
        )

        neighbors.append(neighbor)

    return neighbors

def hex_distance(hex_a, hex_b):
    q1, r1 = hex_a
    q2, r2 = hex_b

    dq = q2 - q1
    dr = r2 - r1

    return max(
        abs(dq),
        abs(dr),
        abs(dq + dr),
    )

def hexes_within_range(center, max_distance):
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

def axial_to_offset(hex_position):
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

def is_hex_on_map(hex_position):
    column, row = axial_to_offset(
        hex_position
    )

    return (
        0 <= column < cfg.GRID_COLUMNS
        and
        0 <= row < cfg.GRID_ROWS
    )

def offset_to_axial(column, row):
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

def axial_to_pixel(hex_position):
    q, r = hex_position

    x = (
        cfg.HEX_SIZE
        * 1.5
        * q
    )

    y = (
        cfg.HEX_SIZE
        * math.sqrt(3)
        * (r + q / 2)
    )

    return (
        x + cfg.GRID_ORIGIN_X,
        y + cfg.GRID_ORIGIN_Y,
    )

def hex_corners(center, size=None):
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
            * math.cos(angle_radians)
        )

        point_y = (
            center_y
            + size
            * math.sin(angle_radians)
        )

        points.append(
            (
                point_x,
                point_y,
            )
        )

    return points