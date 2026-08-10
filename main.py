import pygame

import settings as cfg
from game_state import GameState
from hex_grid import (
    HEX_EDGE_NEIGHBORS,
    axial_to_pixel,
    get_weighted_reachable_hex_data,
    hex_corners,
    is_hex_on_map,
    offset_to_axial,
    pixel_to_axial,
    reconstruct_path,
)
from map_state import (
    BRUSH_ERASER,
    BRUSH_MUD,
    BRUSH_PLAYER_START,
    BRUSH_WALL,
    BRUSH_WATER_DEEP,
    BRUSH_WATER_SHALLOW,
    BRUSH_WATER_VERY_DEEP,
    MapState,
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

clock = pygame.time.Clock()


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

tiny_font = pygame.font.Font(
    None,
    18,
)

path_number_font = pygame.font.Font(
    None,
    18,
)


# --------------------------------------------------
# PANEL POSITION
# --------------------------------------------------

panel_x = (
    cfg.SCREEN_WIDTH
    - cfg.PANEL_WIDTH
)


# --------------------------------------------------
# MAP + GAME STATE
# --------------------------------------------------

map_state = MapState()
state = GameState()

state.start_new_game_session(
    map_state.player_start
)


# --------------------------------------------------
# MODE STATE
# --------------------------------------------------

editor_mode = False
editor_brush = BRUSH_WALL
editor_status = "Editor ready."


# --------------------------------------------------
# SAVED MAP LIST STATE
# --------------------------------------------------

EDITOR_MAPS_PER_PAGE = 4
editor_map_page = 0
editor_pending_load_id = None
editor_pending_new_blank = False
editor_delete_armed = False


# --------------------------------------------------
# MOVEMENT ANIMATION STATE
# --------------------------------------------------

movement_active = False
movement_path = []
movement_path_index = 1
movement_last_step_time = 0


# --------------------------------------------------
# TEXT INPUT STATE
# --------------------------------------------------

active_input = None
energy_input_text = ""
move_input_text = ""
move_speed_input_text = ""
map_name_input_text = ""


# --------------------------------------------------
# GAMEPLAY CONTROL
# --------------------------------------------------

end_turn_rect = pygame.Rect(
    panel_x + 20,
    212,
    255,
    34,
)


# --------------------------------------------------
# GAME DEV CONTROLS
# --------------------------------------------------

reset_turn_rect = pygame.Rect(
    panel_x + 20,
    530,
    120,
    28,
)

reset_player_rect = pygame.Rect(
    panel_x + 155,
    530,
    120,
    28,
)

energy_input_rect = pygame.Rect(
    panel_x + 20,
    584,
    255,
    28,
)

move_input_rect = pygame.Rect(
    panel_x + 20,
    638,
    255,
    28,
)

move_speed_input_rect = pygame.Rect(
    panel_x + 20,
    692,
    255,
    28,
)

path_numbers_rect = pygame.Rect(
    panel_x + 20,
    730,
    120,
    24,
)

map_editor_rect = pygame.Rect(
    panel_x + 155,
    730,
    120,
    24,
)


# --------------------------------------------------
# MAP EDITOR - MAP MANAGEMENT CONTROLS
# --------------------------------------------------

editor_name_input_rect = pygame.Rect(
    panel_x + 20,
    76,
    180,
    30,
)

editor_apply_name_rect = pygame.Rect(
    panel_x + 208,
    76,
    67,
    30,
)

editor_save_map_rect = pygame.Rect(
    panel_x + 20,
    114,
    78,
    30,
)

editor_delete_map_rect = pygame.Rect(
    panel_x + 108,
    114,
    78,
    30,
)

editor_set_default_rect = pygame.Rect(
    panel_x + 196,
    114,
    79,
    30,
)

editor_new_blank_rect = pygame.Rect(
    panel_x + 20,
    152,
    255,
    30,
)


# --------------------------------------------------
# MAP EDITOR - BRUSH CONTROLS
# --------------------------------------------------

editor_wall_rect = pygame.Rect(
    panel_x + 20,
    216,
    120,
    30,
)

editor_mud_rect = pygame.Rect(
    panel_x + 155,
    216,
    120,
    30,
)

editor_shallow_rect = pygame.Rect(
    panel_x + 20,
    252,
    120,
    30,
)

editor_deep_rect = pygame.Rect(
    panel_x + 155,
    252,
    120,
    30,
)

editor_very_deep_rect = pygame.Rect(
    panel_x + 20,
    288,
    120,
    30,
)

editor_eraser_rect = pygame.Rect(
    panel_x + 155,
    288,
    120,
    30,
)

editor_player_start_rect = pygame.Rect(
    panel_x + 20,
    324,
    255,
    30,
)


# --------------------------------------------------
# MAP EDITOR - SAVED MAP LIST
# --------------------------------------------------

editor_map_row_rects = [
    pygame.Rect(
        panel_x + 20,
        404 + row_index * 32,
        255,
        26,
    )
    for row_index in range(
        EDITOR_MAPS_PER_PAGE
    )
]

editor_prev_page_rect = pygame.Rect(
    panel_x + 20,
    534,
    120,
    28,
)

editor_next_page_rect = pygame.Rect(
    panel_x + 155,
    534,
    120,
    28,
)

editor_start_game_rect = pygame.Rect(
    panel_x + 20,
    706,
    255,
    40,
)


# --------------------------------------------------
# DRAW BUTTON
# --------------------------------------------------

def draw_button(
    surface,
    rectangle,
    label,
    font_object,
    mouse_position,
    active=False,
):
    if active:
        colour = cfg.BUTTON_HOVER_COLOR
    elif rectangle.collidepoint(
        mouse_position
    ):
        colour = cfg.BUTTON_HOVER_COLOR
    else:
        colour = cfg.BUTTON_COLOR

    pygame.draw.rect(
        surface,
        colour,
        rectangle,
        border_radius=5,
    )

    if active:
        pygame.draw.rect(
            surface,
            cfg.EDITOR_ACCENT,
            rectangle,
            2,
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
    placeholder="Click, type, Enter",
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
        display_text = text_value
        text_colour = cfg.TEXT_COLOR
    elif active:
        display_text = "|"
        text_colour = cfg.SUBTEXT_COLOR
    else:
        display_text = placeholder
        text_colour = cfg.SUBTEXT_COLOR

    text_surface = font_object.render(
        display_text,
        True,
        text_colour,
    )

    surface.blit(
        text_surface,
        (
            rectangle.x + 8,
            rectangle.y + 6,
        ),
    )


# --------------------------------------------------
# CLEAR TEXT INPUTS
# --------------------------------------------------

def clear_text_inputs():
    global active_input
    global energy_input_text
    global move_input_text
    global move_speed_input_text
    global map_name_input_text

    active_input = None
    energy_input_text = ""
    move_input_text = ""
    move_speed_input_text = ""
    map_name_input_text = ""


# --------------------------------------------------
# APPLY MAP NAME
# --------------------------------------------------

def apply_map_name():
    global active_input
    global map_name_input_text
    global editor_status
    global editor_delete_armed
    global editor_pending_load_id
    global editor_pending_new_blank

    typed_name = (
        map_name_input_text.strip()
    )

    if not typed_name:
        editor_status = (
            "Map name cannot be empty."
        )
        return False

    changed, message = (
        map_state.rename_map(
            typed_name
        )
    )

    editor_status = message

    if changed:
        editor_delete_armed = False
        editor_pending_load_id = None
        editor_pending_new_blank = False

    active_input = None
    map_name_input_text = ""

    return changed


# --------------------------------------------------
# CANCEL MOVEMENT
# --------------------------------------------------

def cancel_movement():
    global movement_active
    global movement_path
    global movement_path_index

    movement_active = False
    movement_path = []
    movement_path_index = 1


# --------------------------------------------------
# TERRAIN DEBUG INFORMATION
# --------------------------------------------------

def terrain_name_and_cost(
    hex_position,
):
    terrain_name = map_state.terrain_at(
        hex_position
    )

    if terrain_name == "wall":
        return "WALL", None

    if terrain_name == "mud":
        return (
            "MUD",
            cfg.MUD_MOVE_COST,
        )

    if terrain_name == "water_shallow":
        return (
            "SHALLOW WATER",
            cfg.WATER_SHALLOW_MOVE_COST,
        )

    if terrain_name == "water_deep":
        return (
            "DEEP WATER",
            cfg.WATER_DEEP_MOVE_COST,
        )

    if terrain_name == "water_very_deep":
        return (
            "VERY DEEP WATER",
            cfg.WATER_VERY_DEEP_MOVE_COST,
        )

    return "GROUND", 1


# --------------------------------------------------
# MAIN LOOP
# --------------------------------------------------

running = True

while running:

    # --------------------------------------------------
    # CURRENT MOUSE POSITION
    # --------------------------------------------------

    mouse_position = (
        pygame.mouse.get_pos()
    )


    # --------------------------------------------------
    # CURRENT SAVED MAP LIBRARY
    # --------------------------------------------------

    saved_maps = (
        map_state.list_saved_maps()
    )

    map_page_count = max(
        1,
        (
            len(saved_maps)
            + EDITOR_MAPS_PER_PAGE
            - 1
        )
        // EDITOR_MAPS_PER_PAGE,
    )

    editor_map_page = max(
        0,
        min(
            editor_map_page,
            map_page_count - 1,
        ),
    )

    page_start = (
        editor_map_page
        * EDITOR_MAPS_PER_PAGE
    )

    page_maps = saved_maps[
        page_start:
        page_start
        + EDITOR_MAPS_PER_PAGE
    ]


    # --------------------------------------------------
    # WINDOW TITLE
    # --------------------------------------------------

    if editor_mode:
        window_mode = "MAP EDITOR"
    else:
        window_mode = "GAME"

    pygame.display.set_caption(
        (
            f"FALLZONE v{cfg.VERSION}"
            f" - {window_mode} - "
            f"{map_state.map_name}"
        )
    )


    # --------------------------------------------------
    # EVENTS
    # --------------------------------------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False
            continue


        # ==================================================
        # MAP EDITOR NAME INPUT
        # ==================================================

        if (
            editor_mode
            and event.type == pygame.KEYDOWN
            and active_input == "map_name"
        ):
            if event.key == pygame.K_RETURN:
                apply_map_name()
                continue

            if event.key == pygame.K_BACKSPACE:
                map_name_input_text = (
                    map_name_input_text[:-1]
                )
                continue

            if event.key == pygame.K_ESCAPE:
                map_name_input_text = ""
                active_input = None
                editor_status = (
                    "Map rename cancelled."
                )
                continue

            if (
                event.unicode
                and event.unicode.isprintable()
                and len(
                    map_name_input_text
                ) < 32
            ):
                map_name_input_text += (
                    event.unicode
                )
                continue


        # ==================================================
        # GAME MODE TEXT INPUT
        # ==================================================

        if (
            not editor_mode
            and event.type == pygame.KEYDOWN
            and active_input is not None
        ):
            if event.key == pygame.K_RETURN:
                if (
                    active_input == "energy"
                    and energy_input_text
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
                    and move_input_text
                ):
                    state.set_session_move_range(
                        int(
                            move_input_text
                        )
                    )
                    move_input_text = ""
                    active_input = None

                elif (
                    active_input == "move_speed"
                    and move_speed_input_text
                ):
                    state.set_session_move_step_ms(
                        int(
                            move_speed_input_text
                        )
                    )
                    move_speed_input_text = ""
                    active_input = None

                else:
                    state.status_message = (
                        "Enter a number first."
                    )

                continue

            if event.key == pygame.K_BACKSPACE:
                if active_input == "energy":
                    energy_input_text = (
                        energy_input_text[:-1]
                    )
                elif active_input == "move":
                    move_input_text = (
                        move_input_text[:-1]
                    )
                elif active_input == "move_speed":
                    move_speed_input_text = (
                        move_speed_input_text[:-1]
                    )
                continue

            if event.key == pygame.K_ESCAPE:
                clear_text_inputs()
                state.status_message = (
                    "Developer input cancelled."
                )
                continue

            if event.unicode.isdigit():
                if (
                    active_input == "energy"
                    and len(
                        energy_input_text
                    ) < 4
                ):
                    energy_input_text += (
                        event.unicode
                    )

                elif (
                    active_input == "move"
                    and len(
                        move_input_text
                    ) < 3
                ):
                    move_input_text += (
                        event.unicode
                    )

                elif (
                    active_input == "move_speed"
                    and len(
                        move_speed_input_text
                    ) < 4
                ):
                    move_speed_input_text += (
                        event.unicode
                    )

                continue


        # ==================================================
        # LEFT MOUSE CLICK
        # ==================================================

        if (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
        ):
            clicked_position = event.pos


            # ==================================================
            # MAP EDITOR MODE
            # ==================================================

            if editor_mode:

                # ------------------------------------------
                # MAP NAME INPUT
                # ------------------------------------------

                if editor_name_input_rect.collidepoint(
                    clicked_position
                ):
                    active_input = "map_name"
                    map_name_input_text = ""
                    editor_delete_armed = False
                    editor_status = (
                        "Type new map name, then Enter or APPLY."
                    )
                    continue


                # ------------------------------------------
                # APPLY MAP NAME
                # ------------------------------------------

                if editor_apply_name_rect.collidepoint(
                    clicked_position
                ):
                    apply_map_name()
                    continue


                # ------------------------------------------
                # SAVE CURRENT MAP
                # ------------------------------------------

                if editor_save_map_rect.collidepoint(
                    clicked_position
                ):
                    # If the tester typed a name and clicks SAVE
                    # without pressing Enter, apply that name first.
                    if (
                        active_input == "map_name"
                        and map_name_input_text.strip()
                    ):
                        apply_map_name()

                    try:
                        path = (
                            map_state.save_current_map()
                        )
                        editor_status = (
                            "Saved map: "
                            f"{path.name}"
                        )
                        editor_delete_armed = False
                        editor_pending_load_id = None
                        editor_pending_new_blank = False

                    except Exception as error:
                        editor_status = (
                            "Save failed: "
                            f"{error}"
                        )

                    continue


                # ------------------------------------------
                # DELETE CURRENT SAVED MAP
                # ------------------------------------------

                if editor_delete_map_rect.collidepoint(
                    clicked_position
                ):
                    clear_text_inputs()

                    if map_state.map_id is None:
                        editor_status = (
                            "This map is not saved, so there is no file to delete."
                        )
                        editor_delete_armed = False

                    elif not editor_delete_armed:
                        editor_delete_armed = True
                        editor_status = (
                            "DELETE armed. Click DELETE again to permanently remove map."
                        )

                    else:
                        try:
                            deleted_path = (
                                map_state.delete_current_map()
                            )
                            editor_status = (
                                "Deleted: "
                                f"{deleted_path.name}. "
                                "New blank map opened."
                            )
                            editor_map_page = 0
                            editor_delete_armed = False
                            editor_pending_load_id = None
                            editor_pending_new_blank = False

                        except Exception as error:
                            editor_status = (
                                "Delete failed: "
                                f"{error}"
                            )
                            editor_delete_armed = False

                    continue


                # ------------------------------------------
                # SAVE + SET AS DEFAULT
                # ------------------------------------------

                if editor_set_default_rect.collidepoint(
                    clicked_position
                ):
                    if (
                        active_input == "map_name"
                        and map_name_input_text.strip()
                    ):
                        apply_map_name()

                    try:
                        path = (
                            map_state.save_as_default()
                        )
                        editor_status = (
                            "Default map saved: "
                            f"{path.name}"
                        )
                        editor_delete_armed = False
                        editor_pending_load_id = None
                        editor_pending_new_blank = False

                    except Exception as error:
                        editor_status = (
                            "Default failed: "
                            f"{error}"
                        )

                    continue


                # ------------------------------------------
                # NEW BLANK MAP
                # ------------------------------------------

                if editor_new_blank_rect.collidepoint(
                    clicked_position
                ):
                    clear_text_inputs()
                    editor_delete_armed = False

                    if (
                        map_state.dirty
                        and not editor_pending_new_blank
                    ):
                        editor_pending_new_blank = True
                        editor_pending_load_id = None
                        editor_status = (
                            "UNSAVED edits. Click NEW BLANK again to discard."
                        )

                    else:
                        map_state.new_blank_map()
                        editor_map_page = 0
                        editor_pending_new_blank = False
                        editor_pending_load_id = None
                        editor_status = (
                            "New blank session map created."
                        )

                    continue


                # ------------------------------------------
                # BRUSH SELECTION
                # ------------------------------------------

                brush_buttons = (
                    (
                        editor_wall_rect,
                        BRUSH_WALL,
                    ),
                    (
                        editor_mud_rect,
                        BRUSH_MUD,
                    ),
                    (
                        editor_shallow_rect,
                        BRUSH_WATER_SHALLOW,
                    ),
                    (
                        editor_deep_rect,
                        BRUSH_WATER_DEEP,
                    ),
                    (
                        editor_very_deep_rect,
                        BRUSH_WATER_VERY_DEEP,
                    ),
                    (
                        editor_eraser_rect,
                        BRUSH_ERASER,
                    ),
                    (
                        editor_player_start_rect,
                        BRUSH_PLAYER_START,
                    ),
                )

                brush_used = False

                for rectangle, brush in brush_buttons:
                    if rectangle.collidepoint(
                        clicked_position
                    ):
                        clear_text_inputs()
                        editor_brush = brush
                        editor_status = (
                            "Selected: "
                            f"{brush.replace('_', ' ')}."
                        )
                        editor_delete_armed = False
                        editor_pending_load_id = None
                        editor_pending_new_blank = False
                        brush_used = True
                        break

                if brush_used:
                    continue


                # ------------------------------------------
                # SAVED MAP LIST ROWS
                # ------------------------------------------

                map_row_used = False

                for row_index, saved_map in enumerate(
                    page_maps
                ):
                    row_rect = (
                        editor_map_row_rects[
                            row_index
                        ]
                    )

                    if row_rect.collidepoint(
                        clicked_position
                    ):
                        clear_text_inputs()
                        editor_delete_armed = False

                        selected_id = (
                            saved_map[
                                "map_id"
                            ]
                        )

                        if selected_id == map_state.map_id:
                            editor_status = (
                                "That map is already loaded."
                            )

                        elif (
                            map_state.dirty
                            and editor_pending_load_id != selected_id
                        ):
                            editor_pending_load_id = selected_id
                            editor_pending_new_blank = False
                            editor_status = (
                                "UNSAVED edits. Click the same map again to discard/load."
                            )

                        else:
                            try:
                                map_state.load_saved_map(
                                    selected_id
                                )
                                editor_pending_load_id = None
                                editor_pending_new_blank = False
                                editor_status = (
                                    "Loaded map: "
                                    f"{map_state.map_name}"
                                )

                            except Exception as error:
                                editor_status = (
                                    "Load failed: "
                                    f"{error}"
                                )

                        map_row_used = True
                        break

                if map_row_used:
                    continue


                # ------------------------------------------
                # PREVIOUS SAVED-MAP PAGE
                # ------------------------------------------

                if editor_prev_page_rect.collidepoint(
                    clicked_position
                ):
                    clear_text_inputs()
                    editor_delete_armed = False
                    editor_map_page = max(
                        0,
                        editor_map_page - 1,
                    )
                    editor_pending_load_id = None
                    editor_pending_new_blank = False
                    continue


                # ------------------------------------------
                # NEXT SAVED-MAP PAGE
                # ------------------------------------------

                if editor_next_page_rect.collidepoint(
                    clicked_position
                ):
                    clear_text_inputs()
                    editor_delete_armed = False
                    editor_map_page = min(
                        map_page_count - 1,
                        editor_map_page + 1,
                    )
                    editor_pending_load_id = None
                    editor_pending_new_blank = False
                    continue


                # ------------------------------------------
                # START GAME SESSION
                # ------------------------------------------

                if editor_start_game_rect.collidepoint(
                    clicked_position
                ):
                    editor_mode = False
                    cancel_movement()
                    clear_text_inputs()
                    editor_delete_armed = False
                    editor_pending_load_id = None
                    editor_pending_new_blank = False
                    state.start_new_game_session(
                        map_state.player_start
                    )
                    continue


                # ------------------------------------------
                # PAINT MAP
                # ------------------------------------------

                if (
                    clicked_position[0]
                    < cfg.PLAY_AREA_WIDTH
                ):
                    clicked_hex = pixel_to_axial(
                        clicked_position
                    )

                    if is_hex_on_map(
                        clicked_hex
                    ):
                        changed, message = (
                            map_state.paint_hex(
                                clicked_hex,
                                editor_brush,
                            )
                        )

                        if changed:
                            editor_delete_armed = False
                            editor_pending_load_id = None
                            editor_pending_new_blank = False

                        editor_status = message

                    continue


            # ==================================================
            # NORMAL GAME MODE
            # ==================================================

            if reset_player_rect.collidepoint(
                clicked_position
            ):
                cancel_movement()
                clear_text_inputs()
                state.reset_player()
                continue

            if path_numbers_rect.collidepoint(
                clicked_position
            ):
                clear_text_inputs()
                state.toggle_path_numbers()
                continue

            if map_editor_rect.collidepoint(
                clicked_position
            ):
                if movement_active:
                    state.status_message = (
                        "Wait for movement to finish before editing."
                    )
                else:
                    clear_text_inputs()
                    editor_mode = True
                    editor_status = (
                        "Editor opened. Session changes are temporary until saved."
                    )
                    editor_delete_armed = False
                    editor_pending_load_id = None
                    editor_pending_new_blank = False
                continue

            if move_speed_input_rect.collidepoint(
                clicked_position
            ):
                active_input = "move_speed"
                move_speed_input_text = ""
                energy_input_text = ""
                move_input_text = ""
                state.status_message = (
                    "Type movement speed in ms and press Enter."
                )
                continue

            if movement_active:
                state.status_message = (
                    "Wait for movement to finish."
                )
                continue

            if end_turn_rect.collidepoint(
                clicked_position
            ):
                clear_text_inputs()
                state.end_turn()
                continue

            if reset_turn_rect.collidepoint(
                clicked_position
            ):
                clear_text_inputs()
                state.reset_turn()
                continue

            if energy_input_rect.collidepoint(
                clicked_position
            ):
                active_input = "energy"
                energy_input_text = ""
                move_input_text = ""
                move_speed_input_text = ""
                state.status_message = (
                    "Type energy and press Enter."
                )
                continue

            if move_input_rect.collidepoint(
                clicked_position
            ):
                active_input = "move"
                move_input_text = ""
                energy_input_text = ""
                move_speed_input_text = ""
                state.status_message = (
                    "Type movement and press Enter."
                )
                continue

            clear_text_inputs()


            # ------------------------------------------
            # CLICK MAP DESTINATION
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
                and is_hex_on_map(
                    clicked_hex
                )
            ):
                if clicked_hex in map_state.wall_hexes:
                    state.status_message = (
                        "Movement blocked by wall."
                    )
                    continue

                terrain_move_costs = (
                    map_state.get_terrain_move_costs()
                )

                energy_limit = (
                    state.player_energy
                    // cfg.MOVE_ENERGY_COST_PER_HEX
                )

                move_budget = min(
                    state.movement_remaining,
                    energy_limit,
                )

                reachable_costs, came_from = (
                    get_weighted_reachable_hex_data(
                        state.player_position,
                        move_budget,
                        map_state.wall_hexes,
                        terrain_move_costs,
                    )
                )

                if (
                    clicked_hex in reachable_costs
                    and clicked_hex != state.player_position
                ):
                    click_path = reconstruct_path(
                        came_from,
                        state.player_position,
                        clicked_hex,
                    )

                    if len(click_path) > 1:
                        movement_active = True
                        movement_path = click_path
                        movement_path_index = 1
                        movement_last_step_time = (
                            pygame.time.get_ticks()
                        )
                        state.status_message = (
                            "Moving. Total path cost: "
                            f"{reachable_costs[clicked_hex]}."
                        )

                elif clicked_hex != state.player_position:
                    state.status_message = (
                        "No affordable path within current movement."
                    )


    # --------------------------------------------------
    # EDITOR CLICK-DRAG PAINTING
    # --------------------------------------------------

    if (
        editor_mode
        and pygame.mouse.get_pressed()[0]
        and mouse_position[0] < cfg.PLAY_AREA_WIDTH
        and editor_brush != BRUSH_PLAYER_START
    ):
        drag_hex = pixel_to_axial(
            mouse_position
        )

        if is_hex_on_map(
            drag_hex
        ):
            changed, message = (
                map_state.paint_hex(
                    drag_hex,
                    editor_brush,
                )
            )

            if changed:
                editor_status = message
                editor_delete_armed = False
                editor_pending_load_id = None
                editor_pending_new_blank = False


    # --------------------------------------------------
    # MOVEMENT ANIMATION UPDATE
    # --------------------------------------------------

    if (
        not editor_mode
        and movement_active
    ):
        current_time = (
            pygame.time.get_ticks()
        )

        if (
            current_time
            - movement_last_step_time
            >= state.session_move_step_ms
        ):
            next_hex = (
                movement_path[
                    movement_path_index
                ]
            )

            terrain_move_costs = (
                map_state.get_terrain_move_costs()
            )

            step_cost = terrain_move_costs.get(
                next_hex,
                1,
            )

            if state.move_player_to(
                next_hex,
                step_cost,
            ):
                movement_path_index += 1
                movement_last_step_time = (
                    current_time
                )

                if (
                    movement_path_index
                    >= len(movement_path)
                ):
                    cancel_movement()
                    state.status_message = (
                        "Movement complete."
                    )

            else:
                cancel_movement()
                state.status_message = (
                    "Movement stopped: insufficient resources."
                )


    # --------------------------------------------------
    # CURRENT MAP / MOUSE DATA
    # --------------------------------------------------

    terrain_move_costs = (
        map_state.get_terrain_move_costs()
    )

    mouse_hex = pixel_to_axial(
        mouse_position
    )

    mouse_hex_on_map = (
        mouse_position[0]
        < cfg.PLAY_AREA_WIDTH
        and is_hex_on_map(
            mouse_hex
        )
    )

    player_center = axial_to_pixel(
        state.player_position
    )


    # --------------------------------------------------
    # DEFAULT GAMEPLAY VISUAL DATA
    # --------------------------------------------------

    preview_path = []
    reachable_hexes = set()
    reachable_costs = {}
    mouse_path_cost = None
    mouse_hex_in_range = False
    player_is_hovered = False
    show_movement_perimeter = False
    current_move_budget = 0


    # --------------------------------------------------
    # GAMEPLAY PATHFINDING / HOVER
    # --------------------------------------------------

    if not editor_mode:
        mouse_dx = (
            mouse_position[0]
            - player_center[0]
        )

        mouse_dy = (
            mouse_position[1]
            - player_center[1]
        )

        player_is_hovered = (
            (
                mouse_dx * mouse_dx
                + mouse_dy * mouse_dy
            ) ** 0.5
            <= cfg.HEX_SIZE * 0.55
        )

        energy_limit = (
            state.player_energy
            // cfg.MOVE_ENERGY_COST_PER_HEX
        )

        current_move_budget = min(
            state.movement_remaining,
            energy_limit,
        )

        reachable_costs, came_from = (
            get_weighted_reachable_hex_data(
                state.player_position,
                current_move_budget,
                map_state.wall_hexes,
                terrain_move_costs,
            )
        )

        reachable_hexes = set(
            reachable_costs.keys()
        )

        mouse_blocked = (
            mouse_hex_on_map
            and mouse_hex in map_state.wall_hexes
        )

        if mouse_hex_on_map:
            mouse_path_cost = (
                reachable_costs.get(
                    mouse_hex
                )
            )

            mouse_hex_in_range = (
                not mouse_blocked
                and mouse_hex != state.player_position
                and mouse_hex in reachable_costs
            )

        if (
            mouse_hex_in_range
            and not movement_active
        ):
            preview_path = reconstruct_path(
                came_from,
                state.player_position,
                mouse_hex,
            )

        show_movement_perimeter = (
            not movement_active
            and current_move_budget > 0
            and (
                player_is_hovered
                or mouse_hex_in_range
            )
        )


    # --------------------------------------------------
    # BACKGROUND
    # --------------------------------------------------

    screen.fill(
        cfg.BACKGROUND
    )


    # --------------------------------------------------
    # DRAW MAP TERRAIN
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

            terrain = map_state.terrain_at(
                hex_position
            )

            if terrain == "wall":
                tile_fill = cfg.WALL_FILL
                tile_outline = cfg.WALL_OUTLINE
                tile_outline_width = cfg.WALL_OUTLINE_WIDTH

            elif terrain == "mud":
                tile_fill = cfg.MUD_FILL
                tile_outline = cfg.MUD_OUTLINE
                tile_outline_width = cfg.MUD_OUTLINE_WIDTH

            elif terrain == "water_very_deep":
                tile_fill = cfg.WATER_VERY_DEEP_FILL
                tile_outline = cfg.WATER_VERY_DEEP_OUTLINE
                tile_outline_width = cfg.WATER_OUTLINE_WIDTH

            elif terrain == "water_deep":
                tile_fill = cfg.WATER_DEEP_FILL
                tile_outline = cfg.WATER_DEEP_OUTLINE
                tile_outline_width = cfg.WATER_OUTLINE_WIDTH

            elif terrain == "water_shallow":
                tile_fill = cfg.WATER_SHALLOW_FILL
                tile_outline = cfg.WATER_SHALLOW_OUTLINE
                tile_outline_width = cfg.WATER_OUTLINE_WIDTH

            else:
                tile_fill = cfg.HEX_FILL
                tile_outline = cfg.HEX_OUTLINE
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


    # ==================================================
    # NORMAL GAME VISUALS
    # ==================================================

    if not editor_mode:

        # --------------------------------------------------
        # BLUE REACHABLE OUTER PERIMETER
        # --------------------------------------------------

        if show_movement_perimeter:
            for hex_position in reachable_hexes:
                q, r = hex_position

                points = hex_corners(
                    axial_to_pixel(
                        hex_position
                    )
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
        # PATH PREVIEW
        # --------------------------------------------------

        if len(preview_path) > 1:
            for path_index in range(
                1,
                len(preview_path),
            ):
                previous_center = axial_to_pixel(
                    preview_path[
                        path_index - 1
                    ]
                )

                current_center = axial_to_pixel(
                    preview_path[
                        path_index
                    ]
                )

                pygame.draw.line(
                    screen,
                    cfg.PATH_PREVIEW_GLOW,
                    previous_center,
                    current_center,
                    7,
                )

                pygame.draw.line(
                    screen,
                    cfg.PATH_PREVIEW,
                    previous_center,
                    current_center,
                    3,
                )

            for step_number, path_hex in enumerate(
                preview_path[1:],
                start=1,
            ):
                path_center = axial_to_pixel(
                    path_hex
                )

                marker_points = hex_corners(
                    path_center,
                    cfg.HEX_SIZE * 0.30,
                )

                pygame.draw.polygon(
                    screen,
                    cfg.PATH_PREVIEW,
                    marker_points,
                )

                if state.dev_show_path_numbers:
                    number_surface = (
                        path_number_font.render(
                            str(step_number),
                            True,
                            cfg.PATH_NUMBER_COLOR,
                        )
                    )

                    number_rect = (
                        number_surface.get_rect(
                            center=(
                                int(path_center[0]),
                                int(path_center[1]),
                            )
                        )
                    )

                    screen.blit(
                        number_surface,
                        number_rect,
                    )


        # --------------------------------------------------
        # DESTINATION HOVER
        # --------------------------------------------------

        if (
            mouse_hex_on_map
            and mouse_hex != state.player_position
            and not movement_active
        ):
            hover_points = hex_corners(
                axial_to_pixel(
                    mouse_hex
                )
            )

            if mouse_hex_in_range:
                soft_colour = cfg.HOVER_VALID_GLOW_SOFT
                bright_colour = cfg.HOVER_VALID_OUTLINE
            else:
                soft_colour = cfg.HOVER_INVALID_GLOW_SOFT
                bright_colour = cfg.HOVER_INVALID_OUTLINE

            pygame.draw.polygon(
                screen,
                soft_colour,
                hover_points,
                7,
            )

            pygame.draw.polygon(
                screen,
                bright_colour,
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


    # ==================================================
    # MAP EDITOR VISUALS
    # ==================================================

    else:
        pygame.draw.rect(
            screen,
            cfg.EDITOR_ACCENT,
            pygame.Rect(
                1,
                1,
                cfg.PLAY_AREA_WIDTH - 2,
                cfg.SCREEN_HEIGHT - 2,
            ),
            4,
        )

        if mouse_hex_on_map:
            hover_points = hex_corners(
                axial_to_pixel(
                    mouse_hex
                )
            )

            pygame.draw.polygon(
                screen,
                cfg.EDITOR_ACCENT,
                hover_points,
                3,
            )

        start_center = axial_to_pixel(
            map_state.player_start
        )

        start_points = hex_corners(
            start_center,
            cfg.HEX_SIZE * 0.55,
        )

        pygame.draw.polygon(
            screen,
            cfg.EDITOR_PLAYER_START,
            start_points,
        )

        pygame.draw.polygon(
            screen,
            cfg.PLAYER_OUTLINE,
            start_points,
            2,
        )

        start_label = tiny_font.render(
            "P",
            True,
            cfg.BACKGROUND,
        )

        screen.blit(
            start_label,
            start_label.get_rect(
                center=start_center
            ),
        )


    # --------------------------------------------------
    # RIGHT PANEL BACKGROUND
    # --------------------------------------------------

    pygame.draw.rect(
        screen,
        cfg.PANEL_COLOR,
        pygame.Rect(
            panel_x,
            0,
            cfg.PANEL_WIDTH,
            cfg.SCREEN_HEIGHT,
        ),
    )


    # ==================================================
    # MAP EDITOR PANEL
    # ==================================================

    if editor_mode:
        editor_title = font.render(
            "MAP EDITOR MODE",
            True,
            cfg.EDITOR_ACCENT,
        )

        screen.blit(
            editor_title,
            (
                panel_x + 20,
                20,
            ),
        )

        if map_state.dirty:
            dirty_text = "UNSAVED"
            dirty_colour = cfg.EDITOR_ACCENT
        else:
            dirty_text = "SAVED"
            dirty_colour = cfg.SUBTEXT_COLOR

        current_name_surface = tiny_font.render(
            (
                "CURRENT: "
                f"{map_state.map_name[:20]} "
                f"[{dirty_text}]"
            ),
            True,
            dirty_colour,
        )

        screen.blit(
            current_name_surface,
            (
                panel_x + 20,
                54,
            ),
        )


        # --------------------------------------------------
        # MAP NAME FIELD + APPLY
        # --------------------------------------------------

        draw_input_box(
            screen,
            editor_name_input_rect,
            map_name_input_text,
            active_input == "map_name",
            tiny_font,
            placeholder="Type new name",
        )

        draw_button(
            screen,
            editor_apply_name_rect,
            "APPLY",
            tiny_font,
            mouse_position,
        )


        # --------------------------------------------------
        # SAVE / DELETE / DEFAULT
        # --------------------------------------------------

        draw_button(
            screen,
            editor_save_map_rect,
            "SAVE",
            tiny_font,
            mouse_position,
        )

        if editor_delete_armed:
            delete_label = "SURE?"
        else:
            delete_label = "DELETE"

        draw_button(
            screen,
            editor_delete_map_rect,
            delete_label,
            tiny_font,
            mouse_position,
            active=editor_delete_armed,
        )

        if map_state.is_current_default():
            default_label = "DEFAULT"
        else:
            default_label = "SET DEF."

        draw_button(
            screen,
            editor_set_default_rect,
            default_label,
            tiny_font,
            mouse_position,
            active=(
                map_state.is_current_default()
            ),
        )

        draw_button(
            screen,
            editor_new_blank_rect,
            "NEW BLANK MAP",
            tiny_font,
            mouse_position,
            active=editor_pending_new_blank,
        )


        # --------------------------------------------------
        # BRUSHES
        # --------------------------------------------------

        brush_title = tiny_font.render(
            (
                "BRUSH: "
                f"{editor_brush.replace('_', ' ').upper()}"
            ),
            True,
            cfg.TEXT_COLOR,
        )

        screen.blit(
            brush_title,
            (
                panel_x + 20,
                196,
            ),
        )

        draw_button(
            screen,
            editor_wall_rect,
            "WALL",
            tiny_font,
            mouse_position,
            active=(
                editor_brush
                == BRUSH_WALL
            ),
        )

        draw_button(
            screen,
            editor_mud_rect,
            "MUD (2)",
            tiny_font,
            mouse_position,
            active=(
                editor_brush
                == BRUSH_MUD
            ),
        )

        draw_button(
            screen,
            editor_shallow_rect,
            "SHALLOW (2)",
            tiny_font,
            mouse_position,
            active=(
                editor_brush
                == BRUSH_WATER_SHALLOW
            ),
        )

        draw_button(
            screen,
            editor_deep_rect,
            "DEEP (3)",
            tiny_font,
            mouse_position,
            active=(
                editor_brush
                == BRUSH_WATER_DEEP
            ),
        )

        draw_button(
            screen,
            editor_very_deep_rect,
            "V.DEEP (4)",
            tiny_font,
            mouse_position,
            active=(
                editor_brush
                == BRUSH_WATER_VERY_DEEP
            ),
        )

        draw_button(
            screen,
            editor_eraser_rect,
            "ERASER",
            tiny_font,
            mouse_position,
            active=(
                editor_brush
                == BRUSH_ERASER
            ),
        )

        draw_button(
            screen,
            editor_player_start_rect,
            "PLAYER START",
            tiny_font,
            mouse_position,
            active=(
                editor_brush
                == BRUSH_PLAYER_START
            ),
        )

        help_surface = tiny_font.render(
            "Left-click / drag map to paint",
            True,
            cfg.SUBTEXT_COLOR,
        )

        screen.blit(
            help_surface,
            (
                panel_x + 20,
                362,
            ),
        )


        # --------------------------------------------------
        # SAVED MAPS
        # --------------------------------------------------

        saved_title = small_font.render(
            "SAVED MAPS",
            True,
            cfg.TEXT_COLOR,
        )

        screen.blit(
            saved_title,
            (
                panel_x + 20,
                382,
            ),
        )

        for row_index, row_rect in enumerate(
            editor_map_row_rects
        ):
            if row_index < len(page_maps):
                saved_map = page_maps[
                    row_index
                ]

                row_name = saved_map[
                    "map_name"
                ]

                if (
                    map_state.map_id
                    == saved_map[
                        "map_id"
                    ]
                ):
                    prefix = "> "

                elif (
                    editor_pending_load_id
                    == saved_map[
                        "map_id"
                    ]
                ):
                    prefix = "! "

                else:
                    prefix = ""

                row_label = (
                    prefix
                    + row_name[:28]
                )

                draw_button(
                    screen,
                    row_rect,
                    row_label,
                    tiny_font,
                    mouse_position,
                    active=(
                        map_state.map_id
                        == saved_map[
                            "map_id"
                        ]
                    ),
                )

            else:
                pygame.draw.rect(
                    screen,
                    cfg.BUTTON_COLOR,
                    row_rect,
                    border_radius=5,
                )

                empty_text = tiny_font.render(
                    "- empty -",
                    True,
                    cfg.SUBTEXT_COLOR,
                )

                screen.blit(
                    empty_text,
                    empty_text.get_rect(
                        center=row_rect.center
                    ),
                )

        draw_button(
            screen,
            editor_prev_page_rect,
            "< PREV",
            tiny_font,
            mouse_position,
        )

        draw_button(
            screen,
            editor_next_page_rect,
            "NEXT >",
            tiny_font,
            mouse_position,
        )

        page_text = tiny_font.render(
            (
                "PAGE "
                f"{editor_map_page + 1}"
                " / "
                f"{map_page_count}"
            ),
            True,
            cfg.SUBTEXT_COLOR,
        )

        screen.blit(
            page_text,
            (
                panel_x + 20,
                568,
            ),
        )


        # --------------------------------------------------
        # CURRENT FILE + STATUS
        # --------------------------------------------------

        if map_state.map_id is None:
            current_file_text = "FILE: not saved yet"
        else:
            current_file_text = (
                "FILE: "
                f"{map_state.map_id}.json"
            )

        file_surface = tiny_font.render(
            current_file_text[:38],
            True,
            cfg.SUBTEXT_COLOR,
        )

        screen.blit(
            file_surface,
            (
                panel_x + 20,
                590,
            ),
        )

        status_line_1 = (
            editor_status[:38]
        )

        status_line_2 = (
            editor_status[38:76]
        )

        status_surface_1 = tiny_font.render(
            status_line_1,
            True,
            cfg.TEXT_COLOR,
        )

        screen.blit(
            status_surface_1,
            (
                panel_x + 20,
                614,
            ),
        )

        if status_line_2:
            status_surface_2 = tiny_font.render(
                status_line_2,
                True,
                cfg.TEXT_COLOR,
            )

            screen.blit(
                status_surface_2,
                (
                    panel_x + 20,
                    634,
                ),
            )

        save_hint = tiny_font.render(
            "Rename + SAVE also renames the JSON file",
            True,
            cfg.SUBTEXT_COLOR,
        )

        screen.blit(
            save_hint,
            (
                panel_x + 20,
                660,
            ),
        )

        draw_button(
            screen,
            editor_start_game_rect,
            "START GAME SESSION",
            small_font,
            mouse_position,
        )


    # ==================================================
    # NORMAL GAME PANEL
    # ==================================================

    else:
        title_text = font.render(
            f"FALLZONE v{cfg.VERSION}",
            True,
            cfg.TEXT_COLOR,
        )

        map_text = tiny_font.render(
            (
                "MAP: "
                f"{map_state.map_name[:28]}"
            ),
            True,
            cfg.SUBTEXT_COLOR,
        )

        hp_text = font.render(
            (
                f"HP: {state.player_hp}"
                f" / {cfg.MAX_HP}"
            ),
            True,
            cfg.TEXT_COLOR,
        )

        energy_text = font.render(
            (
                "ENERGY: "
                f"{state.player_energy}"
                " / "
                f"{state.session_max_energy}"
            ),
            True,
            cfg.TEXT_COLOR,
        )

        position_text = font.render(
            (
                "HEX: "
                f"{state.player_position}"
            ),
            True,
            cfg.TEXT_COLOR,
        )

        turn_text = small_font.render(
            (
                "TURN: "
                f"{state.turn_number}"
            ),
            True,
            cfg.TEXT_COLOR,
        )

        screen.blit(
            title_text,
            (
                panel_x + 24,
                26,
            ),
        )

        screen.blit(
            map_text,
            (
                panel_x + 24,
                60,
            ),
        )

        screen.blit(
            hp_text,
            (
                panel_x + 24,
                88,
            ),
        )

        screen.blit(
            energy_text,
            (
                panel_x + 24,
                120,
            ),
        )

        screen.blit(
            position_text,
            (
                panel_x + 24,
                152,
            ),
        )

        screen.blit(
            turn_text,
            (
                panel_x + 24,
                186,
            ),
        )

        draw_button(
            screen,
            end_turn_rect,
            "END TURN",
            small_font,
            mouse_position,
        )


        # --------------------------------------------------
        # DEBUG DATA
        # --------------------------------------------------

        if mouse_hex_on_map:
            terrain_name, terrain_cost = (
                terrain_name_and_cost(
                    mouse_hex
                )
            )

            mouse_hex_text = (
                "MOUSE HEX: "
                f"{mouse_hex}"
            )
        else:
            terrain_name = "OUTSIDE"
            terrain_cost = None
            mouse_hex_text = (
                "MOUSE HEX: OUTSIDE"
            )

        if not mouse_hex_on_map:
            path_text = "PATH COST: -"
        elif mouse_hex in map_state.wall_hexes:
            path_text = "PATH COST: BLOCKED"
        elif mouse_path_cost is None:
            path_text = "PATH COST: UNREACHABLE"
        else:
            path_text = (
                "PATH COST: "
                f"{mouse_path_cost}"
            )

        if terrain_cost is None:
            terrain_text = (
                "TERRAIN: "
                f"{terrain_name}"
            )
        else:
            terrain_text = (
                "TERRAIN: "
                f"{terrain_name} "
                f"({terrain_cost})"
            )

        debug_lines = (
            "DEVELOPMENT BUILD",
            (
                "PLAYER HOVER: "
                f"{player_is_hovered}"
            ),
            (
                "SESSION MAX MOVE: "
                f"{state.session_max_move_range}"
            ),
            (
                "MOVE LEFT: "
                f"{state.movement_remaining}"
                " / "
                f"{state.session_max_move_range}"
            ),
            (
                "CURRENT BUDGET: "
                f"{current_move_budget}"
            ),
            mouse_hex_text,
            path_text,
            terrain_text,
            state.status_message,
        )

        debug_y_positions = (
            264,
            286,
            308,
            330,
            352,
            382,
            404,
            426,
            458,
        )

        for line, y_position in zip(
            debug_lines,
            debug_y_positions,
        ):
            if "BLOCKED" in line:
                text_colour = (
                    cfg.HOVER_INVALID_OUTLINE
                )
            else:
                text_colour = (
                    cfg.SUBTEXT_COLOR
                )

            line_surface = tiny_font.render(
                line,
                True,
                text_colour,
            )

            screen.blit(
                line_surface,
                (
                    panel_x + 24,
                    y_position,
                ),
            )


        # --------------------------------------------------
        # DEV CONTROLS
        # --------------------------------------------------

        dev_title = small_font.render(
            "DEV CONTROLS",
            True,
            cfg.TEXT_COLOR,
        )

        screen.blit(
            dev_title,
            (
                panel_x + 20,
                500,
            ),
        )

        draw_button(
            screen,
            reset_turn_rect,
            "RESET TURN",
            tiny_font,
            mouse_position,
        )

        draw_button(
            screen,
            reset_player_rect,
            "RESET PLAYER",
            tiny_font,
            mouse_position,
        )

        energy_label = tiny_font.render(
            "SET ENERGY",
            True,
            cfg.TEXT_COLOR,
        )

        screen.blit(
            energy_label,
            (
                panel_x + 20,
                566,
            ),
        )

        draw_input_box(
            screen,
            energy_input_rect,
            energy_input_text,
            active_input == "energy",
            tiny_font,
            placeholder="Type energy, Enter",
        )

        move_label = tiny_font.render(
            "SET MOVE",
            True,
            cfg.TEXT_COLOR,
        )

        screen.blit(
            move_label,
            (
                panel_x + 20,
                620,
            ),
        )

        draw_input_box(
            screen,
            move_input_rect,
            move_input_text,
            active_input == "move",
            tiny_font,
            placeholder="Type move, Enter",
        )

        speed_label = tiny_font.render(
            (
                "SET MOVE SPEED "
                f"({state.session_move_step_ms} ms)"
            ),
            True,
            cfg.TEXT_COLOR,
        )

        screen.blit(
            speed_label,
            (
                panel_x + 20,
                674,
            ),
        )

        draw_input_box(
            screen,
            move_speed_input_rect,
            move_speed_input_text,
            active_input == "move_speed",
            tiny_font,
            placeholder="Type milliseconds, Enter",
        )

        if state.dev_show_path_numbers:
            path_label = "PATH #: ON"
        else:
            path_label = "PATH #: OFF"

        draw_button(
            screen,
            path_numbers_rect,
            path_label,
            tiny_font,
            mouse_position,
        )

        draw_button(
            screen,
            map_editor_rect,
            "MAP EDITOR",
            tiny_font,
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