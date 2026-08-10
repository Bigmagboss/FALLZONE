import settings as cfg

from hex_grid import is_hex_on_map

from map_data import (
    blank_map_data,
    delete_map_data,
    is_default_map,
    list_saved_maps,
    load_default_map_data,
    load_map_data,
    save_map_data,
    set_default_map_id,
)

BRUSH_WALL = 'wall'
BRUSH_MUD = 'mud'
BRUSH_WATER_SHALLOW = 'water_shallow'
BRUSH_WATER_DEEP = 'water_deep'
BRUSH_WATER_VERY_DEEP = 'water_very_deep'
BRUSH_ERASER = 'eraser'
BRUSH_PLAYER_START = 'player_start'


class MapState:

    def __init__(self):
        self.dirty = False
        self.load_data(
            load_default_map_data(),
            dirty=False,
        )

    def load_data(self, data, dirty=False):
        self.map_id = data.get('map_id')

        loaded_name = str(
            data.get(
                'map_name',
                'Untitled Map',
            )
        ).strip()

        if not loaded_name:
            loaded_name = 'Untitled Map'

        self.map_name = loaded_name[:32]
        self.player_start = tuple(data['player_start'])
        self.wall_hexes = set(data['walls'])
        self.mud_hexes = set(data['mud'])
        self.water_shallow_hexes = set(data['water_shallow'])
        self.water_deep_hexes = set(data['water_deep'])
        self.water_very_deep_hexes = set(data['water_very_deep'])
        self.dirty = dirty

    def to_data(self):
        return {
            'map_id': self.map_id,
            'map_name': self.map_name,
            'player_start': self.player_start,
            'walls': set(self.wall_hexes),
            'mud': set(self.mud_hexes),
            'water_shallow': set(self.water_shallow_hexes),
            'water_deep': set(self.water_deep_hexes),
            'water_very_deep': set(self.water_very_deep_hexes),
        }

    def rename_map(self, new_name):
        cleaned_name = str(new_name).strip()

        if not cleaned_name:
            return False, 'Map name cannot be empty.'

        cleaned_name = cleaned_name[:32]

        if cleaned_name == self.map_name:
            return False, f'Map is already named {self.map_name}.'

        self.map_name = cleaned_name
        self.dirty = True

        return True, f'Map renamed to {self.map_name}.'

    def new_blank_map(self):
        self.load_data(
            blank_map_data(),
            dirty=True,
        )

    def load_saved_map(self, map_id):
        self.load_data(
            load_map_data(map_id),
            dirty=False,
        )

    def list_saved_maps(self):
        return list_saved_maps()

    def save_current_map(self):
        saved_id, path = save_map_data(
            self.to_data(),
            self.map_id,
        )
        self.map_id = saved_id
        self.dirty = False
        return path

    def save_as_default(self):
        path = self.save_current_map()
        set_default_map_id(self.map_id)
        return path

    def is_current_default(self):
        return is_default_map(self.map_id)

    def delete_current_map(self):
        if self.map_id is None:
            raise ValueError('Current map has not been saved yet.')

        deleted_path = delete_map_data(
            self.map_id
        )

        self.new_blank_map()

        return deleted_path

    def clear_terrain_at(self, hex_position):
        self.wall_hexes.discard(hex_position)
        self.mud_hexes.discard(hex_position)
        self.water_shallow_hexes.discard(hex_position)
        self.water_deep_hexes.discard(hex_position)
        self.water_very_deep_hexes.discard(hex_position)

    def terrain_at(self, hex_position):
        if hex_position in self.wall_hexes:
            return 'wall'
        if hex_position in self.mud_hexes:
            return 'mud'
        if hex_position in self.water_shallow_hexes:
            return 'water_shallow'
        if hex_position in self.water_deep_hexes:
            return 'water_deep'
        if hex_position in self.water_very_deep_hexes:
            return 'water_very_deep'
        return 'ground'

    def paint_hex(self, hex_position, brush):
        if not is_hex_on_map(hex_position):
            return False, 'Outside map.'

        if brush == BRUSH_PLAYER_START:
            if hex_position in self.wall_hexes:
                return False, 'Player start cannot be inside a wall.'
            if hex_position == self.player_start:
                return False, 'Player start is already here.'
            self.player_start = hex_position
            self.dirty = True
            return True, f'Player start set to {hex_position}.'

        if brush == BRUSH_ERASER:
            if self.terrain_at(hex_position) == 'ground':
                return False, 'Nothing to erase.'
            self.clear_terrain_at(hex_position)
            self.dirty = True
            return True, 'Terrain erased.'

        if brush == BRUSH_WALL and hex_position == self.player_start:
            return False, 'Cannot paint wall over player start.'

        old_terrain = self.terrain_at(hex_position)
        self.clear_terrain_at(hex_position)

        if brush == BRUSH_WALL:
            self.wall_hexes.add(hex_position)
        elif brush == BRUSH_MUD:
            self.mud_hexes.add(hex_position)
        elif brush == BRUSH_WATER_SHALLOW:
            self.water_shallow_hexes.add(hex_position)
        elif brush == BRUSH_WATER_DEEP:
            self.water_deep_hexes.add(hex_position)
        elif brush == BRUSH_WATER_VERY_DEEP:
            self.water_very_deep_hexes.add(hex_position)
        else:
            return False, 'Unknown editor brush.'

        new_terrain = self.terrain_at(hex_position)

        if new_terrain == old_terrain:
            return False, 'Terrain already painted here.'

        self.dirty = True
        return True, f"Painted {new_terrain.replace('_', ' ')}."

    def get_terrain_move_costs(self):
        costs = {}
        costs.update({
            hex_position: cfg.MUD_MOVE_COST
            for hex_position in self.mud_hexes
        })
        costs.update({
            hex_position: cfg.WATER_SHALLOW_MOVE_COST
            for hex_position in self.water_shallow_hexes
        })
        costs.update({
            hex_position: cfg.WATER_DEEP_MOVE_COST
            for hex_position in self.water_deep_hexes
        })
        costs.update({
            hex_position: cfg.WATER_VERY_DEEP_MOVE_COST
            for hex_position in self.water_very_deep_hexes
        })
        return costs