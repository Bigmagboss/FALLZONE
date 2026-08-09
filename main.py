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


# --------------------------------------------------
# PYGAME SETUP
# --------------------------------------------------

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


# --------------------------------------------------
# GAME STATE
# --------------------------------------------------

state = GameState()


# --------------------------------------------------
# FONTS
# --------------------------------------------------

font = pygame.font.Font(
    None,
    30,
)


small_font = pygame.font.Font(
    None,
    22,
)


# --------------------------------------------------
# INFORMATION PANEL
# --------------------------------------------------

panel_x = (
    cfg.SCREEN_WIDTH
    - cfg.PANEL_WIDTH
)


# --------------------------------------------------
# DEVELOPMENT BUTTONS
# --------------------------------------------------

reset_turn_rect = pygame.Rect(
    panel_x + 20,
    535,
    120,
    34,
)


reset_player_rect = pygame.Rect(
    panel_x + 155,
    535,
    120,
    34,
)


energy_down_rect = pygame.Rect(
    panel_x + 20,
    585,
    120,
    34,
)


energy_up_rect = pygame.Rect(
    panel_x + 155,
    585,
    120,
    34,
)


move_down_rect = pygame.Rect(
    panel_x + 20,
    635,
    120,
    34,
)


move_up_rect = pygame.Rect(
    panel_x + 155,
    635,
    120,
    34,
)


# --------------------------------------------------
# DRAW BUTTON FUNCTION
# --------------------------------------------------

def draw_button(
    surface,
    rectangle,
    label,
    font_object,
    mouse_position,
):

    if rectangle.collidepoint(
        mouse_position
    ):
        colour = (
            cfg.BUTTON_HOVER_COLOR
        )

    else:
        colour = (
            cfg.BUTTON_COLOR
        )


    pygame.draw.rect(
        surface,
        colour,
        rectangle,
        border_radius=5,
    )


    label_surface = font_object.render(
        label,
        True,
        cfg.TEXT_COLOR,
    )


    label_rect = label_surface.get_rect(
        center=rectangle.center
    )


    surface.blit(
        label_surface,
        label_rect,
    )


# --------------------------------------------------
# MAIN GAME LOOP
# --------------------------------------------------

running = True


while running:

    # --------------------------------------------------
    # EVENTS
    # --------------------------------------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False


        # --------------------------------------------------
        # LEFT MOUSE CLICK
        # --------------------------------------------------

        if (
            event.type == pygame.MOUSEBUTTONDOWN
            and
            event.button == 1
        ):

            clicked_position = (
                event.pos
            )


            # --------------------------------------------------
            # DEVELOPMENT BUTTONS
            # --------------------------------------------------

            if reset_turn_rect.collidepoint(
                clicked_position
            ):
                state.reset_turn()

                continue


            if reset_player_rect.collidepoint(
                clicked_position
            ):
                state.reset_player()

                continue


            if energy_down_rect.collidepoint(
                clicked_position
            ):
                state.adjust_session_energy(
                    -cfg.DEV_ENERGY_STEP
                )

                continue


            if energy_up_rect.collidepoint(
                clicked_position
            ):
                state.adjust_session_energy(
                    cfg.DEV_ENERGY_STEP
                )

                continue


            if move_down_rect.collidepoint(
                clicked_position
            ):
                state.adjust_session_move_range(
                    -1
                )

                continue


            if move_up_rect.collidepoint(
                clicked_position
            ):
                state.adjust_session_move_range(
                    1
                )

                continue


            # --------------------------------------------------
            # MAP MOVEMENT
            # --------------------------------------------------

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
    # MOUSE POSITION
    # --------------------------------------------------

    mouse_position = pygame.mouse.get_pos()


    # --------------------------------------------------
    # PLAYER SCREEN POSITION
    # --------------------------------------------------

    player_center = axial_to_pixel(
        state.player_position
    )


    # --------------------------------------------------
    # PLAYER HOVER DETECTION
    # --------------------------------------------------

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
    # CALCULATE CURRENT MOVEMENT RANGE
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
    # DECIDE WHETHER TO SHOW BLUE MOVEMENT PERIMETER
    # --------------------------------------------------

    show_movement_perimeter = (
        current_move_range > 0
        and
        (
            player_is_hovered
            or
            mouse_hex_in_range
        )
    )


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
    # DRAW BLUE MOVEMENT RANGE OUTER PERIMETER
    # --------------------------------------------------

    if show_movement_perimeter:

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


                # If another reachable hex exists
                # across this edge, the edge is
                # internal and should NOT glow.
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


                # Soft blue glow.
                pygame.draw.line(
                    screen,
                    cfg.RANGE_GLOW_SOFT,
                    point_a,
                    point_b,
                    7,
                )


                # Bright blue centre.
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
        mouse_hex
        != state.player_position
    ):

        hover_center = axial_to_pixel(
            mouse_hex
        )


        hover_points = hex_corners(
            hover_center
        )


        if mouse_hex_in_range:

            hover_soft_colour = (
                cfg.HOVER_VALID_GLOW_SOFT
            )


            hover_bright_colour = (
                cfg.HOVER_VALID_OUTLINE
            )


        else:

            hover_soft_colour = (
                cfg.HOVER_INVALID_GLOW_SOFT
            )


            hover_bright_colour = (
                cfg.HOVER_INVALID_OUTLINE
            )


        # Soft thick glow.
        pygame.draw.polygon(
            screen,
            hover_soft_colour,
            hover_points,
            7,
        )


        # Bright thin edge.
        pygame.draw.polygon(
            screen,
            hover_bright_colour,
            hover_points,
            2,
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
            f"/ {state.session_max_energy}"
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
            "SESSION MAX MOVE: "
            f"{state.session_max_move_range}"
        ),
        True,
        cfg.SUBTEXT_COLOR,
    )


    movement_left_text = small_font.render(
        (
            "MOVE LEFT: "
            f"{state.movement_remaining} "
            f"/ "
            f"{state.session_max_move_range}"
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


    # --------------------------------------------------
    # CREATE MOUSE DEBUG TEXT
    # --------------------------------------------------

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


    status_text = small_font.render(
        state.status_message,
        True,
        cfg.SUBTEXT_COLOR,
    )


    dev_controls_text = small_font.render(
        "DEV CONTROLS",
        True,
        cfg.TEXT_COLOR,
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
            220,
        ),
    )


    screen.blit(
        hover_text,
        (
            panel_x + 24,
            250,
        ),
    )


    screen.blit(
        range_text,
        (
            panel_x + 24,
            278,
        ),
    )


    screen.blit(
        movement_left_text,
        (
            panel_x + 24,
            306,
        ),
    )


    screen.blit(
        current_range_text,
        (
            panel_x + 24,
            334,
        ),
    )


    screen.blit(
        mouse_hex_text,
        (
            panel_x + 24,
            375,
        ),
    )


    screen.blit(
        distance_text,
        (
            panel_x + 24,
            403,
        ),
    )


    screen.blit(
        valid_text,
        (
            panel_x + 24,
            431,
        ),
    )


    screen.blit(
        status_text,
        (
            panel_x + 24,
            470,
        ),
    )


    # --------------------------------------------------
    # DRAW DEVELOPMENT CONTROLS
    # --------------------------------------------------

    screen.blit(
        dev_controls_text,
        (
            panel_x + 20,
            505,
        ),
    )


    draw_button(
        screen,
        reset_turn_rect,
        "RESET TURN",
        small_font,
        mouse_position,
    )


    draw_button(
        screen,
        reset_player_rect,
        "RESET PLAYER",
        small_font,
        mouse_position,
    )


    draw_button(
        screen,
        energy_down_rect,
        "ENERGY -10",
        small_font,
        mouse_position,
    )


    draw_button(
        screen,
        energy_up_rect,
        "ENERGY +10",
        small_font,
        mouse_position,
    )


    draw_button(
        screen,
        move_down_rect,
        "MOVE -1",
        small_font,
        mouse_position,
    )


    draw_button(
        screen,
        move_up_rect,
        "MOVE +1",
        small_font,
        mouse_position,
    )


    # --------------------------------------------------
    # FINISH FRAME
    # --------------------------------------------------

    pygame.display.flip()


    clock.tick(
        cfg.FPS
    )


pygame.quit()