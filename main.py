import math

import pygame

import settings as cfg
from entities import (
    EDITOR_ENTITY_ORDER,
    ENTITY_TYPES,
    blocked_entity_positions,
    create_entities_from_spawns,
    find_entity_at,
    make_entity_brush,
)
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
    BRUSH_ENTITY_ERASER,
    BRUSH_ERASER,
    BRUSH_MUD,
    BRUSH_PLAYER_START,
    BRUSH_WALL,
    BRUSH_WATER_DEEP,
    BRUSH_WATER_SHALLOW,
    BRUSH_WATER_VERY_DEEP,
    MapState,
)


# SETUP
pygame.init()
screen = pygame.display.set_mode((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 30)
small_font = pygame.font.Font(None, 22)
tiny_font = pygame.font.Font(None, 18)
path_number_font = pygame.font.Font(None, 18)
panel_x = cfg.SCREEN_WIDTH - cfg.PANEL_WIDTH

map_state = MapState()
state = GameState()
state.start_new_game_session(map_state.player_start)
session_entities = create_entities_from_spawns(map_state.get_entity_spawn_data())

editor_mode = False
editor_brush = BRUSH_WALL
editor_status = "Editor ready."
editor_map_page = 0
editor_pending_load_id = None
editor_pending_new_blank = False
editor_delete_armed = False
EDITOR_MAPS_PER_PAGE = 4

movement_active = False
movement_path = []
movement_path_index = 1
movement_last_step_time = 0

active_input = None
energy_input_text = ""
move_input_text = ""
move_speed_input_text = ""
map_name_input_text = ""


# GAME UI
end_turn_rect = pygame.Rect(panel_x + 20, 212, 255, 34)
reset_turn_rect = pygame.Rect(panel_x + 20, 530, 120, 28)
reset_player_rect = pygame.Rect(panel_x + 155, 530, 120, 28)
energy_input_rect = pygame.Rect(panel_x + 20, 584, 255, 28)
move_input_rect = pygame.Rect(panel_x + 20, 638, 255, 28)
move_speed_input_rect = pygame.Rect(panel_x + 20, 692, 255, 28)
path_numbers_rect = pygame.Rect(panel_x + 20, 730, 120, 24)
map_editor_rect = pygame.Rect(panel_x + 155, 730, 120, 24)


# EDITOR UI
editor_name_input_rect = pygame.Rect(panel_x + 20, 68, 180, 30)
editor_apply_name_rect = pygame.Rect(panel_x + 208, 68, 67, 30)
editor_save_map_rect = pygame.Rect(panel_x + 20, 104, 78, 28)
editor_delete_map_rect = pygame.Rect(panel_x + 108, 104, 78, 28)
editor_set_default_rect = pygame.Rect(panel_x + 196, 104, 79, 28)
editor_new_blank_rect = pygame.Rect(panel_x + 20, 138, 255, 28)

editor_wall_rect = pygame.Rect(panel_x + 20, 204, 120, 28)
editor_mud_rect = pygame.Rect(panel_x + 155, 204, 120, 28)
editor_shallow_rect = pygame.Rect(panel_x + 20, 238, 120, 28)
editor_deep_rect = pygame.Rect(panel_x + 155, 238, 120, 28)
editor_very_deep_rect = pygame.Rect(panel_x + 20, 272, 120, 28)
editor_eraser_rect = pygame.Rect(panel_x + 155, 272, 120, 28)

editor_entity_button_rects = {}
for index, entity_type in enumerate(EDITOR_ENTITY_ORDER):
    column = index % 2
    row = index // 2
    x = panel_x + 20 + column * 135
    y = 334 + row * 34
    editor_entity_button_rects[entity_type] = pygame.Rect(x, y, 120, 28)

entity_rows = max(1, math.ceil(len(EDITOR_ENTITY_ORDER) / 2))
editor_entity_eraser_rect = pygame.Rect(
    panel_x + 155,
    334 + (entity_rows - 1) * 34,
    120,
    28,
)
editor_player_start_rect = pygame.Rect(panel_x + 20, 368, 255, 28)

editor_map_row_rects = [
    pygame.Rect(panel_x + 20, 454 + row * 30, 255, 24)
    for row in range(EDITOR_MAPS_PER_PAGE)
]
editor_prev_page_rect = pygame.Rect(panel_x + 20, 576, 120, 26)
editor_next_page_rect = pygame.Rect(panel_x + 155, 576, 120, 26)
editor_start_game_rect = pygame.Rect(panel_x + 20, 712, 255, 36)

TERRAIN_DRAG_BRUSHES = {
    BRUSH_WALL,
    BRUSH_MUD,
    BRUSH_WATER_SHALLOW,
    BRUSH_WATER_DEEP,
    BRUSH_WATER_VERY_DEEP,
    BRUSH_ERASER,
}


# HELPERS
def draw_button(surface, rect, label, font_object, mouse_position, active=False):
    colour = cfg.BUTTON_HOVER_COLOR if active or rect.collidepoint(mouse_position) else cfg.BUTTON_COLOR
    pygame.draw.rect(surface, colour, rect, border_radius=5)
    if active:
        pygame.draw.rect(surface, cfg.EDITOR_ACCENT, rect, 2, border_radius=5)
    text = font_object.render(label, True, cfg.TEXT_COLOR)
    surface.blit(text, text.get_rect(center=rect.center))


def draw_input_box(surface, rect, text_value, active, font_object, placeholder):
    pygame.draw.rect(surface, cfg.BUTTON_COLOR, rect, border_radius=5)
    border = cfg.HOVER_VALID_OUTLINE if active else cfg.HEX_OUTLINE
    pygame.draw.rect(surface, border, rect, 2, border_radius=5)
    if text_value:
        display_text = text_value
        colour = cfg.TEXT_COLOR
    elif active:
        display_text = "|"
        colour = cfg.SUBTEXT_COLOR
    else:
        display_text = placeholder
        colour = cfg.SUBTEXT_COLOR
    text = font_object.render(display_text, True, colour)
    surface.blit(text, (rect.x + 8, rect.y + 6))


def clear_text_inputs():
    global active_input, energy_input_text, move_input_text, move_speed_input_text, map_name_input_text
    active_input = None
    energy_input_text = ""
    move_input_text = ""
    move_speed_input_text = ""
    map_name_input_text = ""


def apply_map_name():
    global active_input, map_name_input_text, editor_status
    global editor_delete_armed, editor_pending_load_id, editor_pending_new_blank

    typed_name = map_name_input_text.strip()
    if not typed_name:
        editor_status = "Map name cannot be empty."
        return False

    changed, message = map_state.rename_map(typed_name)
    editor_status = message
    active_input = None
    map_name_input_text = ""

    if changed:
        editor_delete_armed = False
        editor_pending_load_id = None
        editor_pending_new_blank = False

    return changed


def cancel_movement():
    global movement_active, movement_path, movement_path_index
    movement_active = False
    movement_path = []
    movement_path_index = 1


def rebuild_session_entities():
    global session_entities
    session_entities = create_entities_from_spawns(map_state.get_entity_spawn_data())


def terrain_name_and_cost(hex_position):
    terrain = map_state.terrain_at(hex_position)
    names = {
        "ground": ("GROUND", 1),
        "wall": ("WALL", None),
        "mud": ("MUD", cfg.MUD_MOVE_COST),
        "water_shallow": ("SHALLOW WATER", cfg.WATER_SHALLOW_MOVE_COST),
        "water_deep": ("DEEP WATER", cfg.WATER_DEEP_MOVE_COST),
        "water_very_deep": ("VERY DEEP WATER", cfg.WATER_VERY_DEEP_MOVE_COST),
    }
    return names[terrain]


def draw_actor(surface, position, fill, outline):
    anchor_x, anchor_y = axial_to_pixel(position)
    anchor_x = int(anchor_x)
    anchor_y = int(anchor_y)

    half_body = cfg.ACTOR_BODY_WIDTH // 2
    body_bottom = anchor_y - cfg.ACTOR_BODY_BOTTOM_OFFSET_Y
    body_top = body_bottom - cfg.ACTOR_BODY_HEIGHT
    head_y = anchor_y - cfg.ACTOR_HEAD_OFFSET_Y

    pygame.draw.circle(
        surface,
        cfg.ENTITY_ANCHOR,
        (anchor_x, anchor_y),
        cfg.ACTOR_ANCHOR_RADIUS,
    )

    pygame.draw.line(
        surface,
        outline,
        (
            anchor_x - cfg.ACTOR_LEG_OFFSET_X,
            anchor_y - 2,
        ),
        (
            anchor_x - 3,
            body_bottom,
        ),
        2,
    )

    pygame.draw.line(
        surface,
        outline,
        (
            anchor_x + cfg.ACTOR_LEG_OFFSET_X,
            anchor_y - 2,
        ),
        (
            anchor_x + 3,
            body_bottom,
        ),
        2,
    )

    body_rect = pygame.Rect(
        anchor_x - half_body,
        body_top,
        cfg.ACTOR_BODY_WIDTH,
        cfg.ACTOR_BODY_HEIGHT,
    )

    pygame.draw.rect(
        surface,
        fill,
        body_rect,
        border_radius=3,
    )

    pygame.draw.rect(
        surface,
        outline,
        body_rect,
        2,
        border_radius=3,
    )

    pygame.draw.circle(
        surface,
        fill,
        (
            anchor_x,
            head_y,
        ),
        cfg.ACTOR_HEAD_RADIUS,
    )

    pygame.draw.circle(
        surface,
        outline,
        (
            anchor_x,
            head_y,
        ),
        cfg.ACTOR_HEAD_RADIUS,
        2,
    )


def draw_entity_marker(
    surface,
    entity,
    editor=False,
):

    definition = (
        entity.definition
    )

    anchor_x, anchor_y = (
        axial_to_pixel(
            entity.position
        )
    )

    anchor_x = int(
        anchor_x
    )

    anchor_y = int(
        anchor_y
    )

    if editor:

        pygame.draw.circle(
            surface,
            definition.fill,
            (
                anchor_x,
                anchor_y,
            ),
            9,
        )

        pygame.draw.circle(
            surface,
            definition.outline,
            (
                anchor_x,
                anchor_y,
            ),
            9,
            2,
        )

        label = tiny_font.render(
            definition.short_label,
            True,
            cfg.ENEMY_LABEL,
        )

        surface.blit(
            label,
            label.get_rect(
                center=(
                    anchor_x,
                    anchor_y,
                )
            ),
        )

        return

    draw_actor(
        surface,
        entity.position,
        definition.fill,
        definition.outline,
    )


def actor_sort_key(
    position,
):

    x, y = axial_to_pixel(
        position
    )

    return (
        y,
        x,
    )


def draw_map_terrain():
    for column in range(cfg.GRID_COLUMNS):
        for row in range(cfg.GRID_ROWS):
            hex_position = offset_to_axial(column, row)
            points = hex_corners(axial_to_pixel(hex_position))
            terrain = map_state.terrain_at(hex_position)

            if terrain == "wall":
                fill, outline, width = cfg.WALL_FILL, cfg.WALL_OUTLINE, cfg.WALL_OUTLINE_WIDTH
            elif terrain == "mud":
                fill, outline, width = cfg.MUD_FILL, cfg.MUD_OUTLINE, cfg.MUD_OUTLINE_WIDTH
            elif terrain == "water_shallow":
                fill, outline, width = cfg.WATER_SHALLOW_FILL, cfg.WATER_SHALLOW_OUTLINE, cfg.WATER_OUTLINE_WIDTH
            elif terrain == "water_deep":
                fill, outline, width = cfg.WATER_DEEP_FILL, cfg.WATER_DEEP_OUTLINE, cfg.WATER_OUTLINE_WIDTH
            elif terrain == "water_very_deep":
                fill, outline, width = cfg.WATER_VERY_DEEP_FILL, cfg.WATER_VERY_DEEP_OUTLINE, cfg.WATER_OUTLINE_WIDTH
            else:
                fill, outline, width = cfg.HEX_FILL, cfg.HEX_OUTLINE, 1

            pygame.draw.polygon(screen, fill, points)
            pygame.draw.polygon(screen, outline, points, width)


# MAIN LOOP
running = True
while running:
    mouse_position = pygame.mouse.get_pos()

    saved_maps = map_state.list_saved_maps()
    map_page_count = max(1, math.ceil(len(saved_maps) / EDITOR_MAPS_PER_PAGE))
    editor_map_page = max(0, min(editor_map_page, map_page_count - 1))
    page_start = editor_map_page * EDITOR_MAPS_PER_PAGE
    page_maps = saved_maps[page_start:page_start + EDITOR_MAPS_PER_PAGE]

    mode_name = "MAP EDITOR" if editor_mode else "GAME"
    pygame.display.set_caption(f"FALLZONE v{cfg.VERSION} - {mode_name} - {map_state.map_name}")

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            continue

        # EDITOR NAME INPUT
        if editor_mode and event.type == pygame.KEYDOWN and active_input == "map_name":
            if event.key == pygame.K_RETURN:
                apply_map_name()
            elif event.key == pygame.K_BACKSPACE:
                map_name_input_text = map_name_input_text[:-1]
            elif event.key == pygame.K_ESCAPE:
                map_name_input_text = ""
                active_input = None
                editor_status = "Map rename cancelled."
            elif event.unicode and event.unicode.isprintable() and len(map_name_input_text) < 32:
                map_name_input_text += event.unicode
            continue

        # GAME DEV INPUT
        if not editor_mode and event.type == pygame.KEYDOWN and active_input is not None:
            if event.key == pygame.K_RETURN:
                if active_input == "energy" and energy_input_text:
                    state.set_session_energy(int(energy_input_text))
                    energy_input_text = ""
                    active_input = None
                elif active_input == "move" and move_input_text:
                    state.set_session_move_range(int(move_input_text))
                    move_input_text = ""
                    active_input = None
                elif active_input == "move_speed" and move_speed_input_text:
                    state.set_session_move_step_ms(int(move_speed_input_text))
                    move_speed_input_text = ""
                    active_input = None
                else:
                    state.status_message = "Enter a number first."
                continue

            if event.key == pygame.K_BACKSPACE:
                if active_input == "energy":
                    energy_input_text = energy_input_text[:-1]
                elif active_input == "move":
                    move_input_text = move_input_text[:-1]
                elif active_input == "move_speed":
                    move_speed_input_text = move_speed_input_text[:-1]
                continue

            if event.key == pygame.K_ESCAPE:
                clear_text_inputs()
                state.status_message = "Developer input cancelled."
                continue

            if event.unicode.isdigit():
                if active_input == "energy" and len(energy_input_text) < 4:
                    energy_input_text += event.unicode
                elif active_input == "move" and len(move_input_text) < 3:
                    move_input_text += event.unicode
                elif active_input == "move_speed" and len(move_speed_input_text) < 4:
                    move_speed_input_text += event.unicode
                continue

        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            continue

        clicked_position = event.pos

        # EDITOR CLICKS
        if editor_mode:
            if editor_name_input_rect.collidepoint(clicked_position):
                active_input = "map_name"
                map_name_input_text = ""
                editor_delete_armed = False
                editor_status = "Type new map name, then Enter or APPLY."
                continue

            if editor_apply_name_rect.collidepoint(clicked_position):
                apply_map_name()
                continue

            if editor_save_map_rect.collidepoint(clicked_position):
                if active_input == "map_name" and map_name_input_text.strip():
                    apply_map_name()
                try:
                    path = map_state.save_current_map()
                    editor_status = f"Saved map: {path.name}"
                    editor_delete_armed = False
                    editor_pending_load_id = None
                    editor_pending_new_blank = False
                except Exception as error:
                    editor_status = f"Save failed: {error}"
                continue

            if editor_delete_map_rect.collidepoint(clicked_position):
                if map_state.map_id is None:
                    editor_status = "This temporary map has no saved file to delete."
                    editor_delete_armed = False
                elif not editor_delete_armed:
                    editor_delete_armed = True
                    editor_status = "Click DELETE again to confirm."
                else:
                    try:
                        deleted = map_state.delete_current_map()
                        editor_status = f"Deleted: {deleted.name}"
                        editor_delete_armed = False
                        editor_map_page = 0
                    except Exception as error:
                        editor_status = f"Delete failed: {error}"
                        editor_delete_armed = False
                continue

            if editor_set_default_rect.collidepoint(clicked_position):
                if active_input == "map_name" and map_name_input_text.strip():
                    apply_map_name()
                try:
                    path = map_state.save_as_default()
                    editor_status = f"Default map: {path.name}"
                    editor_delete_armed = False
                except Exception as error:
                    editor_status = f"Default failed: {error}"
                continue

            if editor_new_blank_rect.collidepoint(clicked_position):
                if map_state.dirty and not editor_pending_new_blank:
                    editor_pending_new_blank = True
                    editor_pending_load_id = None
                    editor_status = "UNSAVED edits. Click NEW BLANK again to discard."
                else:
                    map_state.new_blank_map()
                    editor_map_page = 0
                    editor_pending_new_blank = False
                    editor_pending_load_id = None
                    editor_delete_armed = False
                    clear_text_inputs()
                    editor_status = "New blank session map created."
                continue

            terrain_buttons = (
                (editor_wall_rect, BRUSH_WALL),
                (editor_mud_rect, BRUSH_MUD),
                (editor_shallow_rect, BRUSH_WATER_SHALLOW),
                (editor_deep_rect, BRUSH_WATER_DEEP),
                (editor_very_deep_rect, BRUSH_WATER_VERY_DEEP),
                (editor_eraser_rect, BRUSH_ERASER),
                (editor_player_start_rect, BRUSH_PLAYER_START),
                (editor_entity_eraser_rect, BRUSH_ENTITY_ERASER),
            )

            brush_selected = False
            for rect, brush in terrain_buttons:
                if rect.collidepoint(clicked_position):
                    editor_brush = brush
                    editor_status = f"Selected: {brush.replace('_', ' ')}."
                    editor_delete_armed = False
                    editor_pending_load_id = None
                    editor_pending_new_blank = False
                    brush_selected = True
                    break

            if brush_selected:
                continue

            for entity_type, rect in editor_entity_button_rects.items():
                if rect.collidepoint(clicked_position):
                    editor_brush = make_entity_brush(entity_type)
                    editor_status = f"Selected entity: {ENTITY_TYPES[entity_type].label}."
                    editor_delete_armed = False
                    editor_pending_load_id = None
                    editor_pending_new_blank = False
                    brush_selected = True
                    break

            if brush_selected:
                continue

            map_row_used = False
            for row_index, saved_map in enumerate(page_maps):
                row_rect = editor_map_row_rects[row_index]
                if not row_rect.collidepoint(clicked_position):
                    continue

                selected_id = saved_map["map_id"]
                if selected_id == map_state.map_id:
                    editor_status = "That map is already loaded."
                elif map_state.dirty and editor_pending_load_id != selected_id:
                    editor_pending_load_id = selected_id
                    editor_pending_new_blank = False
                    editor_status = "UNSAVED edits. Click the same map again to discard/load."
                else:
                    try:
                        map_state.load_saved_map(selected_id)
                        clear_text_inputs()
                        editor_pending_load_id = None
                        editor_pending_new_blank = False
                        editor_delete_armed = False
                        editor_status = f"Loaded map: {map_state.map_name}"
                    except Exception as error:
                        editor_status = f"Load failed: {error}"
                map_row_used = True
                break

            if map_row_used:
                continue

            if editor_prev_page_rect.collidepoint(clicked_position):
                editor_map_page = max(0, editor_map_page - 1)
                editor_pending_load_id = None
                editor_pending_new_blank = False
                editor_delete_armed = False
                continue

            if editor_next_page_rect.collidepoint(clicked_position):
                editor_map_page = min(map_page_count - 1, editor_map_page + 1)
                editor_pending_load_id = None
                editor_pending_new_blank = False
                editor_delete_armed = False
                continue

            if editor_start_game_rect.collidepoint(clicked_position):
                editor_mode = False
                cancel_movement()
                clear_text_inputs()
                editor_pending_load_id = None
                editor_pending_new_blank = False
                editor_delete_armed = False
                state.start_new_game_session(map_state.player_start)
                rebuild_session_entities()
                continue

            if clicked_position[0] < cfg.PLAY_AREA_WIDTH:
                clicked_hex = pixel_to_axial(clicked_position)
                if is_hex_on_map(clicked_hex):
                    changed, message = map_state.paint_hex(clicked_hex, editor_brush)
                    if changed:
                        editor_delete_armed = False
                        editor_pending_load_id = None
                        editor_pending_new_blank = False
                    editor_status = message
                continue

        # GAME CLICKS
        if reset_player_rect.collidepoint(clicked_position):
            cancel_movement()
            clear_text_inputs()
            state.reset_player()
            continue

        if path_numbers_rect.collidepoint(clicked_position):
            clear_text_inputs()
            state.toggle_path_numbers()
            continue

        if map_editor_rect.collidepoint(clicked_position):
            if movement_active:
                state.status_message = "Wait for movement to finish before editing."
            else:
                clear_text_inputs()
                editor_mode = True
                editor_status = "Editor opened. Session changes are temporary until saved."
                editor_delete_armed = False
                editor_pending_load_id = None
                editor_pending_new_blank = False
            continue

        if move_speed_input_rect.collidepoint(clicked_position):
            active_input = "move_speed"
            move_speed_input_text = ""
            energy_input_text = ""
            move_input_text = ""
            state.status_message = "Type movement speed in ms and press Enter."
            continue

        if movement_active:
            state.status_message = "Wait for movement to finish."
            continue

        if end_turn_rect.collidepoint(clicked_position):
            clear_text_inputs()
            state.end_turn()
            continue

        if reset_turn_rect.collidepoint(clicked_position):
            clear_text_inputs()
            state.reset_turn()
            continue

        if energy_input_rect.collidepoint(clicked_position):
            active_input = "energy"
            energy_input_text = ""
            move_input_text = ""
            move_speed_input_text = ""
            state.status_message = "Type energy and press Enter."
            continue

        if move_input_rect.collidepoint(clicked_position):
            active_input = "move"
            move_input_text = ""
            energy_input_text = ""
            move_speed_input_text = ""
            state.status_message = "Type movement and press Enter."
            continue

        clear_text_inputs()
        clicked_hex = pixel_to_axial(clicked_position)

        if clicked_position[0] >= cfg.PLAY_AREA_WIDTH or not is_hex_on_map(clicked_hex):
            continue

        clicked_entity = find_entity_at(session_entities, clicked_hex)
        if clicked_entity is not None:
            state.status_message = f"Destination occupied by {clicked_entity.definition.label}."
            continue

        if clicked_hex in map_state.wall_hexes:
            state.status_message = "Movement blocked by wall."
            continue

        terrain_move_costs = map_state.get_terrain_move_costs()
        energy_limit = state.player_energy // cfg.MOVE_ENERGY_COST_PER_HEX
        move_budget = min(state.movement_remaining, energy_limit)
        blocked_hexes = map_state.wall_hexes | blocked_entity_positions(session_entities)

        reachable_costs, came_from = get_weighted_reachable_hex_data(
            state.player_position,
            move_budget,
            blocked_hexes,
            terrain_move_costs,
        )

        if clicked_hex in reachable_costs and clicked_hex != state.player_position:
            click_path = reconstruct_path(came_from, state.player_position, clicked_hex)
            if len(click_path) > 1:
                movement_active = True
                movement_path = click_path
                movement_path_index = 1
                movement_last_step_time = pygame.time.get_ticks()
                state.status_message = f"Moving. Total path cost: {reachable_costs[clicked_hex]}."
        elif clicked_hex != state.player_position:
            state.status_message = "No affordable path within current movement."

    # EDITOR DRAG PAINT
    if (
        editor_mode
        and pygame.mouse.get_pressed()[0]
        and mouse_position[0] < cfg.PLAY_AREA_WIDTH
        and editor_brush in TERRAIN_DRAG_BRUSHES
    ):
        drag_hex = pixel_to_axial(mouse_position)
        if is_hex_on_map(drag_hex):
            changed, message = map_state.paint_hex(drag_hex, editor_brush)
            if changed:
                editor_status = message
                editor_delete_armed = False
                editor_pending_load_id = None
                editor_pending_new_blank = False

    # MOVEMENT UPDATE
    if not editor_mode and movement_active:
        current_time = pygame.time.get_ticks()
        if current_time - movement_last_step_time >= state.session_move_step_ms:
            next_hex = movement_path[movement_path_index]
            step_cost = map_state.get_terrain_move_costs().get(next_hex, 1)

            if state.move_player_to(next_hex, step_cost):
                movement_path_index += 1
                movement_last_step_time = current_time
                if movement_path_index >= len(movement_path):
                    cancel_movement()
                    state.status_message = "Movement complete."
            else:
                cancel_movement()
                state.status_message = "Movement stopped: insufficient resources."

    # CURRENT VISUAL DATA
    terrain_move_costs = map_state.get_terrain_move_costs()
    mouse_hex = pixel_to_axial(mouse_position)
    mouse_hex_on_map = (
        mouse_position[0] < cfg.PLAY_AREA_WIDTH
        and is_hex_on_map(mouse_hex)
    )
    player_center = axial_to_pixel(state.player_position)

    preview_path = []
    reachable_hexes = set()
    reachable_costs = {}
    mouse_path_cost = None
    mouse_hex_in_range = False
    player_is_hovered = False
    show_movement_perimeter = False
    current_move_budget = 0
    mouse_entity = None

    if not editor_mode:
        dx = mouse_position[0] - player_center[0]
        dy = mouse_position[1] - player_center[1]
        player_is_hovered = math.hypot(dx, dy) <= cfg.HEX_SIZE * 0.55

        energy_limit = state.player_energy // cfg.MOVE_ENERGY_COST_PER_HEX
        current_move_budget = min(state.movement_remaining, energy_limit)
        blocked_hexes = map_state.wall_hexes | blocked_entity_positions(session_entities)

        reachable_costs, came_from = get_weighted_reachable_hex_data(
            state.player_position,
            current_move_budget,
            blocked_hexes,
            terrain_move_costs,
        )
        reachable_hexes = set(reachable_costs)

        if mouse_hex_on_map:
            mouse_entity = find_entity_at(session_entities, mouse_hex)
            mouse_path_cost = reachable_costs.get(mouse_hex)
            mouse_hex_in_range = (
                mouse_hex != state.player_position
                and mouse_hex not in blocked_hexes
                and mouse_hex in reachable_costs
            )

        if mouse_hex_in_range and not movement_active:
            preview_path = reconstruct_path(came_from, state.player_position, mouse_hex)

        show_movement_perimeter = (
            not movement_active
            and current_move_budget > 0
            and (player_is_hovered or mouse_hex_in_range)
        )

    # DRAW MAP
    screen.fill(cfg.BACKGROUND)
    draw_map_terrain()

    if not editor_mode:
        if show_movement_perimeter:
            for hex_position in reachable_hexes:
                q, r = hex_position
                points = hex_corners(axial_to_pixel(hex_position))
                for edge_index, (dq, dr) in enumerate(HEX_EDGE_NEIGHBORS):
                    neighbor = (q + dq, r + dr)
                    if neighbor in reachable_hexes:
                        continue
                    point_a = points[edge_index]
                    point_b = points[(edge_index + 1) % 6]
                    pygame.draw.line(screen, cfg.RANGE_GLOW_SOFT, point_a, point_b, 7)
                    pygame.draw.line(screen, cfg.RANGE_GLOW, point_a, point_b, 2)

        if len(preview_path) > 1:
            for index in range(1, len(preview_path)):
                previous_center = axial_to_pixel(preview_path[index - 1])
                current_center = axial_to_pixel(preview_path[index])
                pygame.draw.line(screen, cfg.PATH_PREVIEW_GLOW, previous_center, current_center, 7)
                pygame.draw.line(screen, cfg.PATH_PREVIEW, previous_center, current_center, 3)

            for step_number, path_hex in enumerate(preview_path[1:], start=1):
                path_center = axial_to_pixel(path_hex)
                marker = hex_corners(path_center, cfg.HEX_SIZE * 0.30)
                pygame.draw.polygon(screen, cfg.PATH_PREVIEW, marker)
                if state.dev_show_path_numbers:
                    number = path_number_font.render(str(step_number), True, cfg.PATH_NUMBER_COLOR)
                    screen.blit(number, number.get_rect(center=(int(path_center[0]), int(path_center[1]))))

        if mouse_hex_on_map and mouse_hex != state.player_position and not movement_active:
            hover_points = hex_corners(axial_to_pixel(mouse_hex))
            if mouse_hex_in_range:
                soft, bright = cfg.HOVER_VALID_GLOW_SOFT, cfg.HOVER_VALID_OUTLINE
            else:
                soft, bright = cfg.HOVER_INVALID_GLOW_SOFT, cfg.HOVER_INVALID_OUTLINE
            pygame.draw.polygon(screen, soft, hover_points, 7)
            pygame.draw.polygon(screen, bright, hover_points, 2)

        for entity in sorted(session_entities, key=lambda item: axial_to_pixel(item.position)[1]):
            draw_entity_marker(screen, entity)

        actors_to_draw = [
            (
                state.player_position,
                cfg.PLAYER_FILL,
                cfg.PLAYER_OUTLINE,
            )
        ]

        actors_to_draw.extend(
            (
                entity.position,
                entity.definition.fill,
                entity.definition.outline,
            )
            for entity in session_entities
        )

        for (
            position,
            fill,
            outline,
        ) in sorted(
            actors_to_draw,
            key=lambda actor:
            actor_sort_key(
                actor[0]
            ),
        ):

            draw_actor(
                screen,
                position,
                fill,
                outline,
            )

    else:
        pygame.draw.rect(
            screen,
            cfg.EDITOR_ACCENT,
            pygame.Rect(1, 1, cfg.PLAY_AREA_WIDTH - 2, cfg.SCREEN_HEIGHT - 2),
            4,
        )

        if mouse_hex_on_map:
            pygame.draw.polygon(
                screen,
                cfg.EDITOR_ACCENT,
                hex_corners(axial_to_pixel(mouse_hex)),
                3,
            )

        start_center = axial_to_pixel(map_state.player_start)
        start_points = hex_corners(start_center, cfg.HEX_SIZE * 0.55)
        pygame.draw.polygon(screen, cfg.EDITOR_PLAYER_START, start_points)
        pygame.draw.polygon(screen, cfg.PLAYER_OUTLINE, start_points, 2)
        start_label = tiny_font.render("P", True, cfg.BACKGROUND)
        screen.blit(start_label, start_label.get_rect(center=start_center))

        editor_entities = create_entities_from_spawns(map_state.get_entity_spawn_data())
        for entity in editor_entities:
            draw_entity_marker(screen, entity, editor=True)

    # PANEL BACKGROUND
    pygame.draw.rect(
        screen,
        cfg.PANEL_COLOR,
        pygame.Rect(panel_x, 0, cfg.PANEL_WIDTH, cfg.SCREEN_HEIGHT),
    )

    # EDITOR PANEL
    if editor_mode:
        title = font.render("MAP EDITOR MODE", True, cfg.EDITOR_ACCENT)
        screen.blit(title, (panel_x + 20, 16))

        dirty_text = "UNSAVED" if map_state.dirty else "SAVED"
        dirty_colour = cfg.EDITOR_ACCENT if map_state.dirty else cfg.SUBTEXT_COLOR
        current = tiny_font.render(f"CURRENT: {map_state.map_name[:22]} [{dirty_text}]", True, dirty_colour)
        screen.blit(current, (panel_x + 20, 48))

        draw_input_box(
            screen,
            editor_name_input_rect,
            map_name_input_text,
            active_input == "map_name",
            tiny_font,
            "Type new map name",
        )
        draw_button(screen, editor_apply_name_rect, "APPLY", tiny_font, mouse_position)
        draw_button(screen, editor_save_map_rect, "SAVE", tiny_font, mouse_position)
        draw_button(
            screen,
            editor_delete_map_rect,
            "SURE?" if editor_delete_armed else "DELETE",
            tiny_font,
            mouse_position,
            active=editor_delete_armed,
        )
        draw_button(
            screen,
            editor_set_default_rect,
            "DEFAULT" if map_state.is_current_default() else "SET DEF.",
            tiny_font,
            mouse_position,
            active=map_state.is_current_default(),
        )
        draw_button(
            screen,
            editor_new_blank_rect,
            "NEW BLANK MAP",
            tiny_font,
            mouse_position,
            active=editor_pending_new_blank,
        )

        terrain_title = tiny_font.render(f"TERRAIN BRUSH: {editor_brush.replace('_', ' ').upper()[:24]}", True, cfg.TEXT_COLOR)
        screen.blit(terrain_title, (panel_x + 20, 182))

        terrain_buttons = (
            (editor_wall_rect, "WALL", BRUSH_WALL),
            (editor_mud_rect, "MUD (2)", BRUSH_MUD),
            (editor_shallow_rect, "SHALLOW (2)", BRUSH_WATER_SHALLOW),
            (editor_deep_rect, "DEEP (3)", BRUSH_WATER_DEEP),
            (editor_very_deep_rect, "V.DEEP (4)", BRUSH_WATER_VERY_DEEP),
            (editor_eraser_rect, "ERASER", BRUSH_ERASER),
        )
        for rect, label, brush in terrain_buttons:
            draw_button(screen, rect, label, tiny_font, mouse_position, active=editor_brush == brush)

        entity_title = tiny_font.render("ENTITIES", True, cfg.TEXT_COLOR)
        screen.blit(entity_title, (panel_x + 20, 312))

        for entity_type, rect in editor_entity_button_rects.items():
            definition = ENTITY_TYPES[entity_type]
            brush = make_entity_brush(entity_type)
            draw_button(screen, rect, definition.label, tiny_font, mouse_position, active=editor_brush == brush)

        draw_button(
            screen,
            editor_entity_eraser_rect,
            "ENTITY ERASE",
            tiny_font,
            mouse_position,
            active=editor_brush == BRUSH_ENTITY_ERASER,
        )
        draw_button(
            screen,
            editor_player_start_rect,
            "PLAYER START",
            tiny_font,
            mouse_position,
            active=editor_brush == BRUSH_PLAYER_START,
        )

        if mouse_hex_on_map:
            terrain_name, terrain_cost = terrain_name_and_cost(mouse_hex)
            spawn = map_state.entity_spawn_at(mouse_hex)
            entity_text = "NONE" if spawn is None else ENTITY_TYPES.get(spawn["entity_type"], ENTITY_TYPES["enemy"]).label
            hover_text = f"HEX {mouse_hex} | {terrain_name} | ENTITY {entity_text}"
        else:
            hover_text = "HEX OUTSIDE MAP"
        hover_surface = tiny_font.render(hover_text[:39], True, cfg.SUBTEXT_COLOR)
        screen.blit(hover_surface, (panel_x + 20, 404))

        saved_title = small_font.render("SAVED MAPS", True, cfg.TEXT_COLOR)
        screen.blit(saved_title, (panel_x + 20, 430))

        for row_index, row_rect in enumerate(editor_map_row_rects):
            if row_index < len(page_maps):
                saved_map = page_maps[row_index]
                prefix = "> " if saved_map["map_id"] == map_state.map_id else ""
                if saved_map["map_id"] == editor_pending_load_id:
                    prefix = "! "
                draw_button(
                    screen,
                    row_rect,
                    (prefix + saved_map["map_name"])[:30],
                    tiny_font,
                    mouse_position,
                    active=saved_map["map_id"] == map_state.map_id,
                )
            else:
                pygame.draw.rect(screen, cfg.BUTTON_COLOR, row_rect, border_radius=5)

        draw_button(screen, editor_prev_page_rect, "< PREV", tiny_font, mouse_position)
        draw_button(screen, editor_next_page_rect, "NEXT >", tiny_font, mouse_position)
        page_text = tiny_font.render(f"PAGE {editor_map_page + 1} / {map_page_count}", True, cfg.SUBTEXT_COLOR)
        screen.blit(page_text, (panel_x + 20, 606))

        file_text = "not saved yet" if map_state.map_id is None else f"{map_state.map_id}.json"
        file_surface = tiny_font.render(f"FILE: {file_text}"[:39], True, cfg.SUBTEXT_COLOR)
        screen.blit(file_surface, (panel_x + 20, 628))

        status_line_1 = editor_status[:39]
        status_line_2 = editor_status[39:78]
        screen.blit(tiny_font.render(status_line_1, True, cfg.TEXT_COLOR), (panel_x + 20, 650))
        if status_line_2:
            screen.blit(tiny_font.render(status_line_2, True, cfg.TEXT_COLOR), (panel_x + 20, 669))

        count_surface = tiny_font.render(
            f"ENTITIES: {len(map_state.entity_spawns)}",
            True,
            cfg.SUBTEXT_COLOR,
        )
        screen.blit(count_surface, (panel_x + 20, 690))
        draw_button(screen, editor_start_game_rect, "START GAME SESSION", small_font, mouse_position)

    # GAME PANEL
    else:
        title = font.render(f"FALLZONE v{cfg.VERSION}", True, cfg.TEXT_COLOR)
        map_text = tiny_font.render(f"MAP: {map_state.map_name[:28]}", True, cfg.SUBTEXT_COLOR)
        hp_text = font.render(f"HP: {state.player_hp} / {cfg.MAX_HP}", True, cfg.TEXT_COLOR)
        energy_text = font.render(
            f"ENERGY: {state.player_energy} / {state.session_max_energy}",
            True,
            cfg.TEXT_COLOR,
        )
        position_text = font.render(f"HEX: {state.player_position}", True, cfg.TEXT_COLOR)
        turn_text = small_font.render(f"TURN: {state.turn_number}", True, cfg.TEXT_COLOR)

        screen.blit(title, (panel_x + 24, 26))
        screen.blit(map_text, (panel_x + 24, 60))
        screen.blit(hp_text, (panel_x + 24, 88))
        screen.blit(energy_text, (panel_x + 24, 120))
        screen.blit(position_text, (panel_x + 24, 152))
        screen.blit(turn_text, (panel_x + 24, 186))
        draw_button(screen, end_turn_rect, "END TURN", small_font, mouse_position)

        if mouse_hex_on_map:
            terrain_name, terrain_cost = terrain_name_and_cost(mouse_hex)
            mouse_hex_text = f"MOUSE HEX: {mouse_hex}"
            if mouse_entity is not None:
                entity_text = mouse_entity.definition.label
            else:
                entity_text = "NONE"
        else:
            terrain_name, terrain_cost = "OUTSIDE", None
            mouse_hex_text = "MOUSE HEX: OUTSIDE"
            entity_text = "NONE"

        blocked_hexes = map_state.wall_hexes | blocked_entity_positions(session_entities)
        if not mouse_hex_on_map:
            path_text = "PATH COST: -"
        elif mouse_hex in map_state.wall_hexes:
            path_text = "PATH COST: BLOCKED WALL"
        elif mouse_hex in blocked_hexes:
            path_text = "PATH COST: OCCUPIED"
        elif mouse_path_cost is None:
            path_text = "PATH COST: UNREACHABLE"
        else:
            path_text = f"PATH COST: {mouse_path_cost}"

        terrain_text = f"TERRAIN: {terrain_name}" if terrain_cost is None else f"TERRAIN: {terrain_name} ({terrain_cost})"
        debug_lines = (
            "DEVELOPMENT BUILD",
            f"PLAYER HOVER: {player_is_hovered}",
            f"SESSION MAX MOVE: {state.session_max_move_range}",
            f"MOVE LEFT: {state.movement_remaining} / {state.session_max_move_range}",
            f"CURRENT BUDGET: {current_move_budget}",
            mouse_hex_text,
            path_text,
            terrain_text,
            f"ENTITY: {entity_text}",
            state.status_message,
        )
        debug_y = (264, 284, 304, 324, 344, 374, 394, 414, 434, 462)

        for line, y in zip(debug_lines, debug_y):
            colour = cfg.HOVER_INVALID_OUTLINE if "BLOCKED" in line or "OCCUPIED" in line else cfg.SUBTEXT_COLOR
            screen.blit(tiny_font.render(line, True, colour), (panel_x + 24, y))

        screen.blit(small_font.render("DEV CONTROLS", True, cfg.TEXT_COLOR), (panel_x + 20, 500))
        draw_button(screen, reset_turn_rect, "RESET TURN", tiny_font, mouse_position)
        draw_button(screen, reset_player_rect, "RESET PLAYER", tiny_font, mouse_position)

        screen.blit(tiny_font.render("SET ENERGY", True, cfg.TEXT_COLOR), (panel_x + 20, 566))
        draw_input_box(screen, energy_input_rect, energy_input_text, active_input == "energy", tiny_font, "Type energy, Enter")

        screen.blit(tiny_font.render("SET MOVE", True, cfg.TEXT_COLOR), (panel_x + 20, 620))
        draw_input_box(screen, move_input_rect, move_input_text, active_input == "move", tiny_font, "Type move, Enter")

        speed_label = tiny_font.render(f"SET MOVE SPEED ({state.session_move_step_ms} ms)", True, cfg.TEXT_COLOR)
        screen.blit(speed_label, (panel_x + 20, 674))
        draw_input_box(
            screen,
            move_speed_input_rect,
            move_speed_input_text,
            active_input == "move_speed",
            tiny_font,
            "Type milliseconds, Enter",
        )

        path_label = "PATH #: ON" if state.dev_show_path_numbers else "PATH #: OFF"
        draw_button(screen, path_numbers_rect, path_label, tiny_font, mouse_position)
        draw_button(screen, map_editor_rect, "MAP EDITOR", tiny_font, mouse_position)

    pygame.display.flip()
    clock.tick(cfg.FPS)

pygame.quit()