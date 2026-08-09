import pygame

import settings as cfg

from game_state import GameState

from hex_grid import (
    HEX_EDGE_NEIGHBORS,
    axial_to_pixel,
    hex_corners,
    hex_distance,
    hexes_within_range,
    is_hex_on_map,
    offset_to_axial,
    pixel_to_axial,
)

pygame.init()

screen = pygame.display.set_mode(
    (
        cfg.SCREEN_WIDTH,
        cfg.SCREEN_HEIGHT,
    )
)

pygame.display.set_caption(
    f"FALLZONE v{cfg.VERSION}"
)

clock = pygame.time.Clock()

state = GameState()

font = pygame.font.Font(
    None,
    30,
)

small_font = pygame.font.Font(
    None,
    22,
)

running = True


while running:

    # --------------------------------------------------
    # EVENTS
    # --------------------------------------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False


        if (
            event.type == pygame.MOUSEBUTTONDOWN
            and
            event.button == 1
        ):

            clicked_position = event.pos

            clicked_hex = pixel_to_axial(
                clicked_position
            )

            clicked_inside_play_area = (
                clicked_position[0]
                < cfg.PLAY_AREA_WIDTH
            )

            if (
                clicked_inside_play_area
                and
                is_hex_on_map(
                    clicked_hex
                )
            ):

                clicked_distance = hex_distance(
                    state.player_position,
                    clicked_hex,
                )

                if state.can_move(
                    clicked_distance
                ):

                    state.move_player_to(
                        clicked_hex,
                        clicked_distance,
                    )


    # --------------------------------------------------
    # MOUSE / PLAYER HOVER
    # --------------------------------------------------

    mouse_position = pygame.mouse.get_pos()

    player_center = axial_to_pixel(
        state.player_position
    )

    mouse_dx = (
        mouse_position[0]
        - player_center[0]
    )

    mouse_dy = (
        mouse_position[1]
        - player_center[1]
    )

    mouse_distance_from_player = (
        mouse_dx * mouse_dx
        + mouse_dy * mouse_dy
    ) ** 0.5

    player_is_hovered = (
        mouse_distance_from_player
        <= cfg.HEX_SIZE * 0.55
    )


    # --------------------------------------------------
    # IDENTIFY HEX UNDER MOUSE
    # --------------------------------------------------

    mouse_hex = pixel_to_axial(
        mouse_position
    )

    mouse_hex_on_map = (
        mouse_position[0]
        < cfg.PLAY_AREA_WIDTH
        and
        is_hex_on_map(
            mouse_hex
        )
    )

    if mouse_hex_on_map:

        mouse_hex_distance = hex_distance(
            state.player_position,
            mouse_hex,
        )

        mouse_hex_in_range = (
            1
            <= mouse_hex_distance
            <= current_move_range
        )

    else:

        mouse_hex_distance = None
        mouse_hex_in_range = False


    # --------------------------------------------------
    # CALCULATE MOVEMENT RANGE
    # --------------------------------------------------

    energy_move_limit = (
        state.player_energy
        // cfg.MOVE_ENERGY_COST_PER_HEX
    )

    current_move_range = min(
        state.movement_remaining,
        energy_move_limit,
    )
    
    reachable_hexes = hexes_within_range(
        state.player_position,
        current_move_range,
    )

    reachable_hexes = {
        hex_position
        for hex_position in reachable_hexes
        if is_hex_on_map(
            hex_position
        )
    }


    # --------------------------------------------------
    # DRAW BACKGROUND
    # --------------------------------------------------

    screen.fill(
        cfg.BACKGROUND
    )


    # --------------------------------------------------
    # DRAW HEX GRID
    # --------------------------------------------------

    for column in range(
        cfg.GRID_COLUMNS
    ):

        for row in range(
            cfg.GRID_ROWS
        ):

            hex_position = offset_to_axial(
                column,
                row,
            )

            center = axial_to_pixel(
                hex_position
            )

            points = hex_corners(
                center
            )

            pygame.draw.polygon(
                screen,
                cfg.HEX_FILL,
                points,
            )

            pygame.draw.polygon(
                screen,
                cfg.HEX_OUTLINE,
                points,
                1,
            )


    # --------------------------------------------------
    # DRAW MOVEMENT RANGE OUTER PERIMETER
    # --------------------------------------------------

    if (
        player_is_hovered
        and
        current_move_range > 0
    ):

        for hex_position in reachable_hexes:

            q, r = hex_position

            center = axial_to_pixel(
                hex_position
            )

            points = hex_corners(
                center
            )

            for edge_index, (
                dq,
                dr,
            ) in enumerate(
                HEX_EDGE_NEIGHBORS
            ):

                neighbor = (
                    q + dq,
                    r + dr,
                )

                # If another reachable hex is beside this
                # edge, this is an INTERNAL edge.
                #
                # Therefore we do NOT glow it.
                if neighbor in reachable_hexes:
                    continue

                point_a = points[
                    edge_index
                ]

                point_b = points[
                    (
                        edge_index + 1
                    ) % 6
                ]

                # Soft, thick outer glow.
                pygame.draw.line(
                    screen,
                    cfg.RANGE_GLOW_SOFT,
                    point_a,
                    point_b,
                    7,
                )

                # Bright, thin centre line.
                pygame.draw.line(
                    screen,
                    cfg.RANGE_GLOW,
                    point_a,
                    point_b,
                    2,
                )


    # --------------------------------------------------
    # DRAW HOVERED DESTINATION HEX
    # --------------------------------------------------

    if (
        mouse_hex_on_map
        and
        mouse_hex != state.player_position
    ):

        hover_center = axial_to_pixel(
            mouse_hex
        )

        hover_points = hex_corners(
            hover_center
        )

        if mouse_hex_in_range:
            hover_colour = (
                cfg.HOVER_VALID_OUTLINE
            )

        else:
            hover_colour = (
                cfg.HOVER_INVALID_OUTLINE
            )

            pygame.draw.polygon(
                screen,
                hover_colour,
                hover_points,
                3,
            )

    # --------------------------------------------------
    # DRAW PLAYER
    # --------------------------------------------------

    player_points = hex_corners(
        player_center,
        cfg.HEX_SIZE * 0.55,
    )

    pygame.draw.polygon(
        screen,
        cfg.PLAYER_FILL,
        player_points,
    )

    pygame.draw.polygon(
        screen,
        cfg.PLAYER_OUTLINE,
        player_points,
        2,
    )


    # --------------------------------------------------
    # DRAW INFORMATION PANEL
    # --------------------------------------------------

    panel_x = (
        cfg.SCREEN_WIDTH
        - cfg.PANEL_WIDTH
    )

    panel_rect = pygame.Rect(
        panel_x,
        0,
        cfg.PANEL_WIDTH,
        cfg.SCREEN_HEIGHT,
    )

    pygame.draw.rect(
        screen,
        cfg.PANEL_COLOR,
        panel_rect,
    )


    # --------------------------------------------------
    # CREATE MAIN HUD TEXT
    # --------------------------------------------------

    title_text = font.render(
        f"FALLZONE v{cfg.VERSION}",
        True,
        cfg.TEXT_COLOR,
    )

    hp_text = font.render(
        (
            f"HP: "
            f"{state.player_hp} "
            f"/ {cfg.MAX_HP}"
        ),
        True,
        cfg.TEXT_COLOR,
    )

    energy_text = font.render(
        (
            f"ENERGY: "
            f"{state.player_energy} "
            f"/ {cfg.MAX_ENERGY}"
        ),
        True,
        cfg.TEXT_COLOR,
    )

    position_text = font.render(
        (
            f"HEX: "
            f"{state.player_position}"
        ),
        True,
        cfg.TEXT_COLOR,
    )


    # --------------------------------------------------
    # CREATE DEBUG TEXT
    # --------------------------------------------------

    debug_title = small_font.render(
        "DEVELOPMENT BUILD",
        True,
        cfg.SUBTEXT_COLOR,
    )

    hover_text = small_font.render(
        (
            "PLAYER HOVER: "
            f"{player_is_hovered}"
        ),
        True,
        cfg.SUBTEXT_COLOR,
    )

    range_text = small_font.render(
        (
            "MAX MOVE RANGE: "
            f"{cfg.MAX_MOVE_RANGE}"
        ),
        True,
        cfg.SUBTEXT_COLOR,
    )

    movement_left_text = small_font.render(
        (
            "MOVE LEFT: "
            f"{state.movement_remaining} "
            f"/ {cfg.MAX_MOVE_RANGE}"
        ),
        True,
        cfg.SUBTEXT_COLOR,
    )

    current_range_text = small_font.render(
        (
            "CURRENT RANGE: "
            f"{current_move_range}"
        ),
        True,
        cfg.SUBTEXT_COLOR,
    )

    if mouse_hex_on_map:

        mouse_hex_text = small_font.render(
            (
                "MOUSE HEX: "
                f"{mouse_hex}"
            ),
            True,
            cfg.SUBTEXT_COLOR,
        )

        distance_text = small_font.render(
            (
                "DISTANCE: "
                f"{mouse_hex_distance}"
            ),
            True,
            cfg.SUBTEXT_COLOR,
        )

    else:

        mouse_hex_text = small_font.render(
            "MOUSE HEX: OUTSIDE",
            True,
            cfg.SUBTEXT_COLOR,
        )

        distance_text = small_font.render(
            "DISTANCE: -",
            True,
            cfg.SUBTEXT_COLOR,
        )


    valid_text = small_font.render(
        (
            "IN RANGE: "
            f"{mouse_hex_in_range}"
        ),
        True,
        cfg.SUBTEXT_COLOR,
    )


    # --------------------------------------------------
    # DRAW MAIN HUD TEXT
    # --------------------------------------------------

    screen.blit(
        title_text,
        (
            panel_x + 24,
            32,
        ),
    )

    screen.blit(
        hp_text,
        (
            panel_x + 24,
            90,
        ),
    )

    screen.blit(
        energy_text,
        (
            panel_x + 24,
            130,
        ),
    )

    screen.blit(
        position_text,
        (
            panel_x + 24,
            170,
        ),
    )


    # --------------------------------------------------
    # DRAW DEBUG TEXT
    # --------------------------------------------------

    screen.blit(
        debug_title,
        (
            panel_x + 24,
            230,
        ),
    )

    screen.blit(
        hover_text,
        (
            panel_x + 24,
            270,
        ),
    )

    screen.blit(
        range_text,
        (
            panel_x + 24,
            300,
        ),
    )

    screen.blit(
        movement_left_text,
        (
            panel_x + 24,
            330,
        ),
    )

    screen.blit(
        current_range_text,
        (
            panel_x + 24,
            360,
        ),
    )

    screen.blit(
        mouse_hex_text,
        (
            panel_x + 24,
            340,
        ),
    )

    screen.blit(
        distance_text,
        (
            panel_x + 24,
            370,
        ),
    )

    screen.blit(
        valid_text,
        (
            panel_x + 24,
            400,
        ),
    )


    # --------------------------------------------------
    # FINISH FRAME
    # --------------------------------------------------

    pygame.display.flip()

    clock.tick(
        cfg.FPS
    )


pygame.quit()