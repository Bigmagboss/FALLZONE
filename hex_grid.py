import heapq
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
    return [(q + dq, r + dr) for dq, dr in HEX_DIRECTIONS]


def offset_to_axial(column, row):
    q = column
    r = row - (column - (column & 1)) // 2
    return q, r


def axial_to_offset(hex_position):
    q, r = hex_position
    column = q
    row = r + (q - (q & 1)) // 2
    return column, row


def is_hex_on_map(hex_position):
    column, row = axial_to_offset(hex_position)
    return (
        0 <= column < cfg.GRID_COLUMNS
        and 0 <= row < cfg.GRID_ROWS
    )


def axial_to_pixel(hex_position):
    q, r = hex_position
    x = cfg.HEX_SIZE * 1.5 * q
    y = cfg.HEX_SIZE * math.sqrt(3) * (r + q / 2)
    return x + cfg.GRID_ORIGIN_X, y + cfg.GRID_ORIGIN_Y


def axial_round(q_float, r_float):
    x = q_float
    z = r_float
    y = -x - z

    rounded_x = round(x)
    rounded_y = round(y)
    rounded_z = round(z)

    x_difference = abs(rounded_x - x)
    y_difference = abs(rounded_y - y)
    z_difference = abs(rounded_z - z)

    if x_difference > y_difference and x_difference > z_difference:
        rounded_x = -rounded_y - rounded_z
    elif y_difference > z_difference:
        rounded_y = -rounded_x - rounded_z
    else:
        rounded_z = -rounded_x - rounded_y

    return int(rounded_x), int(rounded_z)


def pixel_to_axial(pixel_position):
    pixel_x, pixel_y = pixel_position
    local_x = pixel_x - cfg.GRID_ORIGIN_X
    local_y = pixel_y - cfg.GRID_ORIGIN_Y

    q_float = (2 / 3) * local_x / cfg.HEX_SIZE
    r_float = (
        (-1 / 3) * local_x / cfg.HEX_SIZE
        + (math.sqrt(3) / 3) * local_y / cfg.HEX_SIZE
    )

    return axial_round(q_float, r_float)


def hex_corners(center, size=None):
    center_x, center_y = center
    size = cfg.HEX_SIZE if size is None else size
    points = []

    for corner in range(6):
        angle = math.radians(60 * corner)
        points.append(
            (
                center_x + size * math.cos(angle),
                center_y + size * math.sin(angle),
            )
        )

    return points


def get_weighted_reachable_hex_data(
    start,
    max_cost,
    blocked_hexes,
    terrain_costs,
):
    costs = {start: 0}
    came_from = {start: None}
    frontier = [(0, start)]

    while frontier:
        current_cost, current = heapq.heappop(frontier)

        if current_cost != costs.get(current):
            continue
        if current_cost > max_cost:
            continue

        for neighbor in get_neighbors(current):
            if neighbor in blocked_hexes:
                continue
            if not is_hex_on_map(neighbor):
                continue

            step_cost = terrain_costs.get(neighbor, 1)
            new_cost = current_cost + step_cost

            if new_cost > max_cost:
                continue

            if neighbor not in costs or new_cost < costs[neighbor]:
                costs[neighbor] = new_cost
                came_from[neighbor] = current
                heapq.heappush(frontier, (new_cost, neighbor))

    return costs, came_from


def reconstruct_path(came_from, start, destination):
    if destination not in came_from:
        return []

    path = []
    current = destination

    while current is not None:
        path.append(current)
        if current == start:
            break
        current = came_from.get(current)

    if not path or path[-1] != start:
        return []

    path.reverse()
    return path