import pygame

import settings as cfg

from game_state import GameState

from map_data import WALL_HEXES

from hex_grid import (
    HEX_EDGE_NEIGHBORS,
    axial_to_pixel,
    get_reachable_hex_distances,
    hex_corners,
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
# RIGHT INFORMATION PANEL
# --------------------------------------------------

panel_x = (
    cfg.SCREEN_WIDTH
    - cfg.PANEL_WIDTH
)


# --------------------------------------------------
# DEVELOPER CONTROLS
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


energy_input_rect = pygame.Rect(
    panel_x + 20,
    605,
    255,
    34,
)


move_input_rect = pygame.Rect(
    panel_x + 20,
    675,
    255,
    34,
)


# --------------------------------------------------
# TEXT INPUT STATE
# --------------------------------------------------

active_input = None

energy_input_text = ""

move_input_text = ""


# --------------------------------------------------
# DRAW BUTTON
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
# DRAW TEXT INPUT
# --------------------------------------------------

def draw_input_box(
    surface,
    rectangle,
    text_value,
    active,
    font_object,
):

    pygame.draw.rect(
        surface,
        cfg.BUTTON_COLOR,
        rectangle,
        border_radius=5,
    )

    if active:

        border_colour = (
            cfg.HOVER_VALID_OUTLINE
        )

    else:

        border_colour = (
            cfg.HEX_OUTLINE
        )

    pygame.draw.rect(
        surface,
        border_colour,
        rectangle,
        2,
        border_radius=5,
    )

    if text_value:

        display_text = (
            text_value
        )

        text_colour = (
            cfg.TEXT_COLOR
        )

    else:

        if active:

            display_text = "|"

        else:

            display_text = (
                "Click, type number, Enter"
            )

        text_colour = (
            cfg.SUBTEXT_COLOR
        )

    text_surface = font_object.render(
        display_text,
        True,
        text_colour,
    )

    surface.blit(
        text_surface,
        (
            rectangle.x + 10,
            rectangle.y + 7,
        ),
    )


# --------------------------------------------------
# MAIN LOOP
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
        # DEV TEXT INPUT
        # --------------------------------------------------

        if (
            event.type == pygame.KEYDOWN
            and
            active_input is not None
        ):

            # ------------------------------------------
            # ENTER
            # ------------------------------------------

            if event.key == pygame.K_RETURN:

                if (
                    active_input == "energy"
                    and
                    energy_input_text
                ):

                    state.set_session_energy(
                        int(
                            energy_input_text
                        )
                    )

                    energy_input_text = ""

                    active_input = None

                elif (
                    active_input == "move"
                    and
                    move_input_text
                ):

                    state.set_session_move_range(
                        int(
                            move_input_text
                        )
                    )

                    move_input_text = ""

                    active_input = None

                else:

                    state.status_message = (
                        "Enter a number first."
                    )

                continue


            # ------------------------------------------
            # BACKSPACE
            # ------------------------------------------

            if event.key == pygame.K_BACKSPACE:

                if active_input == "energy":

                    energy_input_text = (
                        energy_input_text[:-1]
                    )

                elif active_input == "move":

                    move_input_text = (
                        move_input_text[:-1]
                    )

                continue


            # ------------------------------------------
            # ESCAPE
            # ------------------------------------------

            if event.key == pygame.K_ESCAPE:

                active_input = None

                energy_input_text = ""

                move_input_text = ""

                state.status_message = (
                    "Developer input cancelled."
                )

                continue


            # ------------------------------------------
            # DIGITS ONLY
            # ------------------------------------------

            if event.unicode.isdigit():

                if active_input == "energy":

                    if (
                        len(
                            energy_input_text
                        )
                        < 4
                    ):

                        energy_input_text += (
                            event.unicode
                        )

                elif active_input == "move":

                    if (
                        len(
                            move_input_text
                        )
                        < 3
                    ):

                        move_input_text += (
                            event.unicode
                        )

                continue


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


            # ------------------------------------------
            # RESET TURN
            # ------------------------------------------

            if reset_turn_rect.collidepoint(
                clicked_position
            ):

                active_input = None

                state.reset_turn()

                continue


            # ------------------------------------------
            # RESET PLAYER
            # ------------------------------------------

            if reset_player_rect.collidepoint(
                clicked_position
            ):

                active_input = None

                state.reset_player()

                continue


            # ------------------------------------------
            # ENERGY INPUT
            # ------------------------------------------

            if energy_input_rect.collidepoint(
                clicked_position
            ):

                active_input = (
                    "energy"
                )

                energy_input_text = ""

                move_input_text = ""

                state.status_message = (
                    "Type energy and press Enter."
                )

                continue


            # ------------------------------------------
            # MOVE INPUT
            # ------------------------------------------

            if move_input_rect.collidepoint(
                clicked_position
            ):

                active_input = (
                    "move"
                )

                move_input_text = ""

                energy_input_text = ""

                state.status_message = (
                    "Type movement and press Enter."
                )

                continue


            active_input = None


            # ------------------------------------------
            # MAP MOVEMENT
            # ------------------------------------------

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

                # --------------------------------------
                # WALL CLICK
                # --------------------------------------

                if clicked_hex in WALL_HEXES:

                    state.status_message = (
                        "Movement blocked by wall."
                    )

                    continue


                # --------------------------------------
                # CURRENT RESOURCE LIMIT
                # --------------------------------------

                click_energy_limit = (
                    state.player_energy
                    // cfg.MOVE_ENERGY_COST_PER_HEX
                )

                click_move_range = min(
                    state.movement_remaining,
                    click_energy_limit,
                )


                # --------------------------------------
                # BFS REACHABILITY
                # --------------------------------------

                click_reachable_distances = (
                    get_reachable_hex_distances(
                        state.player_position,
                        click_move_range,
                        WALL_HEXES,
                    )
                )


                # --------------------------------------
                # MOVE
                # --------------------------------------

                if (
                    clicked_hex
                    in click_reachable_distances
                    and
                    clicked_hex
                    != state.player_position
                ):

                    movement_cost = (
                        click_reachable_distances[
                            clicked_hex
                        ]
                    )

                    state.move_player_to(
                        clicked_hex,
                        movement_cost,
                    )

                elif (
                    clicked_hex
                    != state.player_position
                ):

                    state.status_message = (
                        "No reachable path "
                        "within current movement."
                    )


    # --------------------------------------------------
    # MOUSE POSITION
    # --------------------------------------------------

    mouse_position = (
        pygame.mouse.get_pos()
    )


    # --------------------------------------------------
    # PLAYER PIXEL POSITION
    # --------------------------------------------------

    player_center = axial_to_pixel(
        state.player_position
    )


    # --------------------------------------------------
    # PLAYER HOVER
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
    # CURRENT MOVEMENT RANGE
    # --------------------------------------------------

    energy_move_limit = (
        state.player_energy
        // cfg.MOVE_ENERGY_COST_PER_HEX
    )

    current_move_range = min(
        state.movement_remaining,
        energy_move_limit,
    )


    # --------------------------------------------------
    # BFS REACHABLE AREA
    # --------------------------------------------------

    reachable_distances = (
        get_reachable_hex_distances(
            state.player_position,
            current_move_range,
            WALL_HEXES,
        )
    )

    reachable_hexes = set(
        reachable_distances.keys()
    )


    # --------------------------------------------------
    # HEX UNDER MOUSE
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

    mouse_hex_blocked = (
        mouse_hex_on_map
        and
        mouse_hex in WALL_HEXES
    )


    # --------------------------------------------------
    # MOUSE DESTINATION DATA
    # --------------------------------------------------

    if mouse_hex_on_map:

        mouse_hex_distance = (
            reachable_distances.get(
                mouse_hex
            )
        )

        mouse_hex_in_range = (
            not mouse_hex_blocked
            and
            mouse_hex
            != state.player_position
            and
            mouse_hex
            in reachable_distances
        )

    else:

        mouse_hex_distance = None

        mouse_hex_in_range = False


    # --------------------------------------------------
    # BLUE RANGE VISIBILITY
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
    # BACKGROUND
    # --------------------------------------------------

    screen.fill(
        cfg.BACKGROUND
    )


    # --------------------------------------------------
    # DRAW MAP
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


            # ------------------------------------------
            # WALL TILE
            # ------------------------------------------

            if hex_position in WALL_HEXES:

                tile_fill = (
                    cfg.WALL_FILL
                )

                tile_outline = (
                    cfg.WALL_OUTLINE
                )

                tile_outline_width = (
                    cfg.WALL_OUTLINE_WIDTH
                )


            # ------------------------------------------
            # NORMAL TILE
            # ------------------------------------------

            else:

                tile_fill = (
                    cfg.HEX_FILL
                )

                tile_outline = (
                    cfg.HEX_OUTLINE
                )

                tile_outline_width = 1


            pygame.draw.polygon(
                screen,
                tile_fill,
                points,
            )

            pygame.draw.polygon(
                screen,
                tile_outline,
                points,
                tile_outline_width,
            )


    # --------------------------------------------------
    # BLUE REACHABLE OUTER PERIMETER
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

                # Internal reachable edge:
                # do not draw it.
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

                pygame.draw.line(
                    screen,
                    cfg.RANGE_GLOW_SOFT,
                    point_a,
                    point_b,
                    7,
                )

                pygame.draw.line(
                    screen,
                    cfg.RANGE_GLOW,
                    point_a,
                    point_b,
                    2,
                )


    # --------------------------------------------------
    # HOVERED DESTINATION
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


        # ----------------------------------------------
        # GREEN: ACTUALLY REACHABLE
        # ----------------------------------------------

        if mouse_hex_in_range:

            hover_soft_colour = (
                cfg.HOVER_VALID_GLOW_SOFT
            )

            hover_bright_colour = (
                cfg.HOVER_VALID_OUTLINE
            )


        # ----------------------------------------------
        # RED: INVALID / WALL / UNREACHABLE
        # ----------------------------------------------

        else:

            hover_soft_colour = (
                cfg.HOVER_INVALID_GLOW_SOFT
            )

            hover_bright_colour = (
                cfg.HOVER_INVALID_OUTLINE
            )


        pygame.draw.polygon(
            screen,
            hover_soft_colour,
            hover_points,
            7,
        )

        pygame.draw.polygon(
            screen,
            hover_bright_colour,
            hover_points,
            2,
        )


    # --------------------------------------------------
    # PLAYER
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
    # INFORMATION PANEL
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
    # MAIN HUD TEXT
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
    # DEBUG TEXT
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
    # MOUSE DEBUG TEXT
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


        if mouse_hex_blocked:

            distance_text = small_font.render(
                "PATH COST: BLOCKED",
                True,
                cfg.HOVER_INVALID_OUTLINE,
            )

        elif mouse_hex_distance is None:

            distance_text = small_font.render(
                "PATH COST: UNREACHABLE",
                True,
                cfg.SUBTEXT_COLOR,
            )

        else:

            distance_text = small_font.render(
                (
                    "PATH COST: "
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
            "PATH COST: -",
            True,
            cfg.SUBTEXT_COLOR,
        )


    if mouse_hex_blocked:

        valid_text = small_font.render(
            "DESTINATION: WALL",
            True,
            cfg.HOVER_INVALID_OUTLINE,
        )

    else:

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


    # --------------------------------------------------
    # DEV CONTROL TEXT
    # --------------------------------------------------

    dev_controls_text = small_font.render(
        "DEV CONTROLS",
        True,
        cfg.TEXT_COLOR,
    )

    energy_label_text = small_font.render(
        "SET ENERGY",
        True,
        cfg.TEXT_COLOR,
    )

    move_label_text = small_font.render(
        "SET MOVE",
        True,
        cfg.TEXT_COLOR,
    )


    # --------------------------------------------------
    # DRAW HUD
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
    # DRAW DEBUG INFORMATION
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
    # DRAW DEV CONTROLS
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

    screen.blit(
        energy_label_text,
        (
            panel_x + 20,
            582,
        ),
    )

    draw_input_box(
        screen,
        energy_input_rect,
        energy_input_text,
        active_input == "energy",
        small_font,
    )

    screen.blit(
        move_label_text,
        (
            panel_x + 20,
            652,
        ),
    )

    draw_input_box(
        screen,
        move_input_rect,
        move_input_text,
        active_input == "move",
        small_font,
    )


    # --------------------------------------------------
    # FINISH FRAME
    # --------------------------------------------------

    pygame.display.flip()

    clock.tick(
        cfg.FPS
    )


pygame.quit()