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

def hex_corners(center):
    center_x, center_y = center


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
            + cfg.HEX_SIZE
            * math.cos(angle_radians)
        )

        point_y = (
            center_y
            + cfg.HEX_SIZE
            * math.sin(angle_radians)
        )

        points.append(
            (
                point_x,
                point_y,
            )
        )

    return points