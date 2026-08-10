import heapq
import math

from collections import deque

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


# Same six neighbours, but ordered to match
# the polygon edges produced by hex_corners().
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

def get_neighbors(
    hex_position
):

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
# DIRECT HEX DISTANCE
# --------------------------------------------------

def hex_distance(
    hex_a,
    hex_b,
):

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
# SIMPLE HEX RANGE
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
# BFS OBSTACLE-AWARE REACHABILITY
# --------------------------------------------------

def get_reachable_hex_data(
    start,
    max_steps,
    blocked_hexes,
):

    # Distance from player to each discovered hex.
    distances = {
        start: 0
    }


    # Stores which hex led to each discovered hex.
    #
    # Example:
    #
    # came_from[(12, 4)] = (11, 4)
    #
    # This lets us reconstruct the actual route later.

    came_from = {
        start: None
    }


    frontier = deque(
        [
            start
        ]
    )


    while frontier:

        current = frontier.popleft()

        current_distance = (
            distances[
                current
            ]
        )


        # Do not search beyond available movement.

        if (
            current_distance
            >= max_steps
        ):

            continue


        for neighbor in get_neighbors(
            current
        ):

            # ------------------------------------------
            # BLOCKED HEX
            # ------------------------------------------

            if neighbor in blocked_hexes:

                continue


            # ------------------------------------------
            # OUTSIDE MAP
            # ------------------------------------------

            if not is_hex_on_map(
                neighbor
            ):

                continue


            # ------------------------------------------
            # ALREADY DISCOVERED
            # ------------------------------------------

            if neighbor in distances:

                continue


            next_distance = (
                current_distance
                + 1
            )


            distances[
                neighbor
            ] = next_distance


            came_from[
                neighbor
            ] = current


            frontier.append(
                neighbor
            )


    return (
        distances,
        came_from,
    )


# --------------------------------------------------
# DISTANCE-ONLY BFS COMPATIBILITY FUNCTION
# --------------------------------------------------

def get_reachable_hex_distances(
    start,
    max_steps,
    blocked_hexes,
):

    distances, _ = (
        get_reachable_hex_data(
            start,
            max_steps,
            blocked_hexes,
        )
    )

    return distances


# --------------------------------------------------
# WEIGHTED DIJKSTRA REACHABILITY
# --------------------------------------------------

def get_weighted_reachable_hex_data(
    start,
    max_cost,
    blocked_hexes,
    terrain_costs,
):

    # Total movement cost required to reach
    # every discovered hex.

    costs = {
        start: 0
    }


    # Used later to reconstruct the chosen
    # cheapest path.

    came_from = {
        start: None
    }


    # Priority queue.
    #
    # Lower-cost positions are explored first.

    frontier = [
        (
            0,
            start,
        )
    ]


    while frontier:

        current_cost, current = (
            heapq.heappop(
                frontier
            )
        )


        # Ignore an outdated queue entry if a cheaper
        # route to this same hex has already been found.

        if (
            current_cost
            != costs.get(
                current
            )
        ):
            continue


        if current_cost > max_cost:
            continue


        for neighbor in get_neighbors(
            current
        ):

            # --------------------------------------------------
            # WALL / BLOCKED HEX
            # --------------------------------------------------

            if neighbor in blocked_hexes:
                continue


            # --------------------------------------------------
            # OUTSIDE MAP
            # --------------------------------------------------

            if not is_hex_on_map(
                neighbor
            ):
                continue


            # --------------------------------------------------
            # TERRAIN MOVEMENT COST
            # --------------------------------------------------

            step_cost = terrain_costs.get(
                neighbor,
                1,
            )


            new_cost = (
                current_cost
                + step_cost
            )


            # Destination would exceed the available
            # movement budget.

            if new_cost > max_cost:
                continue


            # --------------------------------------------------
            # FIRST ROUTE OR CHEAPER ROUTE
            # --------------------------------------------------

            if (
                neighbor not in costs
                or
                new_cost
                < costs[
                    neighbor
                ]
            ):

                costs[
                    neighbor
                ] = new_cost


                came_from[
                    neighbor
                ] = current


                heapq.heappush(
                    frontier,
                    (
                        new_cost,
                        neighbor,
                    ),
                )


    return (
        costs,
        came_from,
    )



# --------------------------------------------------
# RECONSTRUCT BFS PATH
# --------------------------------------------------

def reconstruct_path(
    came_from,
    start,
    destination,
):

    if destination not in came_from:

        return []


    path = []

    current = (
        destination
    )


    while current is not None:

        path.append(
            current
        )


        if current == start:

            break


        current = came_from.get(
            current
        )


    if (
        not path
        or
        path[-1] != start
    ):

        return []


    path.reverse()


    return path


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

        size = (
            cfg.HEX_SIZE
        )


    points = []


    for corner in range(6):

        angle_degrees = (
            60 * corner
        )


        angle_radians = (
            math.radians(
                angle_degrees
            )
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