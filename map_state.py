import settings as cfg
from entities import ENTITY_TYPES, entity_type_from_brush
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


BRUSH_WALL = "wall"
BRUSH_MUD = "mud"
BRUSH_WATER_SHALLOW = "water_shallow"
BRUSH_WATER_DEEP = "water_deep"
BRUSH_WATER_VERY_DEEP = "water_very_deep"
BRUSH_ERASER = "eraser"
BRUSH_PLAYER_START = "player_start"
BRUSH_ENTITY_ERASER = "entity_eraser"


class MapState:
    def __init__(self):
        self.dirty = False
        self.load_data(load_default_map_data(), dirty=False)

    def load_data(self, data, dirty=False):
        self.map_id = data.get("map_id")
        loaded_name = str(data.get("map_name", "Untitled Map")).strip()
        self.map_name = (loaded_name or "Untitled Map")[:32]
        self.player_start = tuple(data["player_start"])
        self.wall_hexes = set(data["walls"])
        self.mud_hexes = set(data["mud"])
        self.water_shallow_hexes = set(data["water_shallow"])
        self.water_deep_hexes = set(data["water_deep"])
        self.water_very_deep_hexes = set(data["water_very_deep"])
        self.entity_spawns = {}

        for spawn in data.get("entities", []):
            entity_id = str(spawn["entity_id"])
            self.entity_spawns[entity_id] = {
                "entity_id": entity_id,
                "entity_type": str(spawn["entity_type"]),
                "position": tuple(spawn["position"]),
            }

        self.dirty = dirty

    def to_data(self):
        return {
            "map_id": self.map_id,
            "map_name": self.map_name,
            "player_start": self.player_start,
            "walls": set(self.wall_hexes),
            "mud": set(self.mud_hexes),
            "water_shallow": set(self.water_shallow_hexes),
            "water_deep": set(self.water_deep_hexes),
            "water_very_deep": set(self.water_very_deep_hexes),
            "entities": self.get_entity_spawn_data(),
        }

    def rename_map(self, new_name):
        cleaned_name = str(new_name).strip()[:32]
        if not cleaned_name:
            return False, "Map name cannot be empty."
        if cleaned_name == self.map_name:
            return False, f"Map is already named {self.map_name}."

        self.map_name = cleaned_name
        self.dirty = True
        return True, f"Map renamed to {self.map_name}."

    def new_blank_map(self):
        self.load_data(blank_map_data(), dirty=True)

    def load_saved_map(self, map_id):
        self.load_data(load_map_data(map_id), dirty=False)

    def list_saved_maps(self):
        return list_saved_maps()

    def save_current_map(self):
        saved_id, path = save_map_data(self.to_data(), self.map_id)
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
            raise ValueError("Current map has not been saved yet.")
        deleted_path = delete_map_data(self.map_id)
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
            return "wall"
        if hex_position in self.mud_hexes:
            return "mud"
        if hex_position in self.water_shallow_hexes:
            return "water_shallow"
        if hex_position in self.water_deep_hexes:
            return "water_deep"
        if hex_position in self.water_very_deep_hexes:
            return "water_very_deep"
        return "ground"

    def get_entity_spawn_data(self):
        return [
            {
                "entity_id": spawn["entity_id"],
                "entity_type": spawn["entity_type"],
                "position": tuple(spawn["position"]),
            }
            for spawn in sorted(
                self.entity_spawns.values(),
                key=lambda item: item["entity_id"],
            )
        ]

    def entity_spawn_at(self, hex_position):
        for spawn in self.entity_spawns.values():
            if spawn["position"] == hex_position:
                return spawn
        return None

    def entity_spawn_positions(self):
        return {spawn["position"] for spawn in self.entity_spawns.values()}

    def _next_entity_id(self, entity_type):
        number = 1
        while f"{entity_type}_{number}" in self.entity_spawns:
            number += 1
        return f"{entity_type}_{number}"

    def place_entity(self, hex_position, entity_type):
        if entity_type not in ENTITY_TYPES:
            return False, f"Unknown entity type: {entity_type}."
        if hex_position in self.wall_hexes:
            return False, "Entity cannot be placed inside a wall."
        if hex_position == self.player_start:
            return False, "Entity cannot overlap player start."
        if self.entity_spawn_at(hex_position) is not None:
            return False, "Another entity is already here."

        entity_id = self._next_entity_id(entity_type)
        self.entity_spawns[entity_id] = {
            "entity_id": entity_id,
            "entity_type": entity_type,
            "position": tuple(hex_position),
        }
        self.dirty = True
        return True, f"Placed {ENTITY_TYPES[entity_type].label}: {entity_id}."

    def erase_entity_at(self, hex_position):
        spawn = self.entity_spawn_at(hex_position)
        if spawn is None:
            return False, "No removable entity here."

        del self.entity_spawns[spawn["entity_id"]]
        self.dirty = True
        return True, f"Removed {spawn['entity_id']}."

    def paint_hex(self, hex_position, brush):
        if not is_hex_on_map(hex_position):
            return False, "Outside map."

        entity_type = entity_type_from_brush(brush)
        if entity_type is not None:
            return self.place_entity(hex_position, entity_type)

        if brush == BRUSH_ENTITY_ERASER:
            return self.erase_entity_at(hex_position)

        if brush == BRUSH_PLAYER_START:
            if hex_position in self.wall_hexes:
                return False, "Player start cannot be inside a wall."
            if self.entity_spawn_at(hex_position) is not None:
                return False, "Player start cannot overlap an entity."
            if hex_position == self.player_start:
                return False, "Player start is already here."
            self.player_start = hex_position
            self.dirty = True
            return True, f"Player start set to {hex_position}."

        if brush == BRUSH_ERASER:
            if self.terrain_at(hex_position) == "ground":
                return False, "Nothing to erase."
            self.clear_terrain_at(hex_position)
            self.dirty = True
            return True, "Terrain erased."

        if brush == BRUSH_WALL:
            if hex_position == self.player_start:
                return False, "Cannot paint wall over player start."
            if self.entity_spawn_at(hex_position) is not None:
                return False, "Cannot paint wall over an entity."

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
            return False, "Unknown editor brush."

        new_terrain = self.terrain_at(hex_position)
        if new_terrain == old_terrain:
            return False, "Terrain already painted here."

        self.dirty = True
        return True, f"Painted {new_terrain.replace('_', ' ')}."

    def get_terrain_move_costs(self):
        costs = {
            hex_position: cfg.MUD_MOVE_COST
            for hex_position in self.mud_hexes
        }
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