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