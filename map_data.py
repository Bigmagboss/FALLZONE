import json
import re
from pathlib import Path

import settings as cfg
from hex_grid import offset_to_axial


MAPS_DIR = Path(__file__).resolve().parent / "maps"
DEFAULT_MAP_POINTER_PATH = MAPS_DIR / "default_map.txt"
LEGACY_DEFAULT_MAP_PATH = MAPS_DIR / "default_map.json"


def _rect_hexes(column_start, column_end, row_start, row_end):
    return {
        offset_to_axial(column, row)
        for column in range(column_start, column_end)
        for row in range(row_start, row_end)
    }


BUILTIN_WALL_HEXES = _rect_hexes(13, 15, 5, 15)
BUILTIN_MUD_HEXES = _rect_hexes(19, 24, 8, 13)
_water_all = _rect_hexes(20, 25, 2, 7)
_water_deep_or_more = _rect_hexes(21, 24, 3, 6)
BUILTIN_WATER_VERY_DEEP_HEXES = {offset_to_axial(22, 4)}
BUILTIN_WATER_DEEP_HEXES = _water_deep_or_more - BUILTIN_WATER_VERY_DEEP_HEXES
BUILTIN_WATER_SHALLOW_HEXES = _water_all - _water_deep_or_more


def _hexes_from_json(values):
    return {tuple(value) for value in values}


def _sorted_hexes(values):
    return [list(value) for value in sorted(values)]


def _clean_map_name(name):
    cleaned = str(name).strip()
    return (cleaned or "Untitled Map")[:32]


def _safe_map_id(value):
    base = re.sub(r"[^a-z0-9]+", "_", str(value).strip().lower()).strip("_")
    return (base or "map")[:40]


def _map_path(map_id):
    return MAPS_DIR / f"{_safe_map_id(map_id)}.json"


def _unique_map_id(desired_id, ignore_id=None):
    desired_id = _safe_map_id(desired_id)
    ignore_id = _safe_map_id(ignore_id) if ignore_id is not None else None
    candidate_id = desired_id
    number = 2

    while _map_path(candidate_id).exists() and candidate_id != ignore_id:
        candidate_id = f"{desired_id}_{number}"
        number += 1

    return candidate_id


def _normalise_entities(raw):
    entities = []

    for index, entry in enumerate(raw.get("entities", []), start=1):
        if not isinstance(entry, dict):
            continue
        if "entity_type" not in entry or "position" not in entry:
            continue
        entities.append(
            {
                "entity_id": str(entry.get("entity_id", f"entity_{index}")),
                "entity_type": str(entry["entity_type"]),
                "position": tuple(entry["position"]),
            }
        )

    if not entities:
        for index, position in enumerate(raw.get("enemy_spawns", []), start=1):
            entities.append(
                {
                    "entity_id": f"enemy_{index}",
                    "entity_type": "enemy",
                    "position": tuple(position),
                }
            )

    return entities


def _normalise_map_data(raw, map_id=None):
    fallback_name = map_id.replace("_", " ").title() if map_id else "Built-in Test Map"
    return {
        "map_id": map_id,
        "map_name": _clean_map_name(raw.get("map_name", fallback_name)),
        "player_start": tuple(raw.get("player_start", cfg.PLAYER_START)),
        "walls": _hexes_from_json(raw.get("walls", [])),
        "mud": _hexes_from_json(raw.get("mud", [])),
        "water_shallow": _hexes_from_json(raw.get("water_shallow", [])),
        "water_deep": _hexes_from_json(raw.get("water_deep", [])),
        "water_very_deep": _hexes_from_json(raw.get("water_very_deep", [])),
        "entities": _normalise_entities(raw),
    }


def built_in_map_data():
    return {
        "map_id": None,
        "map_name": "Built-in Test Map",
        "player_start": tuple(cfg.PLAYER_START),
        "walls": set(BUILTIN_WALL_HEXES),
        "mud": set(BUILTIN_MUD_HEXES),
        "water_shallow": set(BUILTIN_WATER_SHALLOW_HEXES),
        "water_deep": set(BUILTIN_WATER_DEEP_HEXES),
        "water_very_deep": set(BUILTIN_WATER_VERY_DEEP_HEXES),
        "entities": [],
    }


def blank_map_data():
    return {
        "map_id": None,
        "map_name": "Untitled Map",
        "player_start": tuple(cfg.PLAYER_START),
        "walls": set(),
        "mud": set(),
        "water_shallow": set(),
        "water_deep": set(),
        "water_very_deep": set(),
        "entities": [],
    }


def list_saved_maps():
    if not MAPS_DIR.exists():
        return []

    saved_maps = []
    for path in MAPS_DIR.glob("*.json"):
        try:
            with path.open("r", encoding="utf-8") as file:
                raw = json.load(file)
            saved_maps.append(
                {
                    "map_id": path.stem,
                    "map_name": _clean_map_name(
                        raw.get("map_name", path.stem.replace("_", " ").title())
                    ),
                }
            )
        except (OSError, json.JSONDecodeError):
            continue

    saved_maps.sort(key=lambda item: (item["map_name"].casefold(), item["map_id"]))
    return saved_maps


def load_map_data(map_id):
    path = _map_path(map_id)
    if not path.exists():
        raise FileNotFoundError(f"Saved map not found: {map_id}")

    with path.open("r", encoding="utf-8") as file:
        raw = json.load(file)

    return _normalise_map_data(raw, path.stem)


def get_default_map_id():
    if DEFAULT_MAP_POINTER_PATH.exists():
        map_id = DEFAULT_MAP_POINTER_PATH.read_text(encoding="utf-8").strip()
        if map_id and _map_path(map_id).exists():
            return _safe_map_id(map_id)

    if LEGACY_DEFAULT_MAP_PATH.exists():
        return "default_map"

    return None


def set_default_map_id(map_id):
    safe_id = _safe_map_id(map_id)
    if not _map_path(safe_id).exists():
        raise FileNotFoundError("Save the map before making it default.")

    MAPS_DIR.mkdir(parents=True, exist_ok=True)
    DEFAULT_MAP_POINTER_PATH.write_text(safe_id, encoding="utf-8")
    return safe_id


def is_default_map(map_id):
    return map_id is not None and get_default_map_id() == _safe_map_id(map_id)


def save_map_data(data, map_id=None):
    MAPS_DIR.mkdir(parents=True, exist_ok=True)

    map_name = _clean_map_name(data.get("map_name", "Untitled Map"))
    old_id = _safe_map_id(map_id) if map_id is not None else None
    target_id = _unique_map_id(_safe_map_id(map_name), ignore_id=old_id)
    old_was_default = old_id is not None and get_default_map_id() == old_id
    target_path = _map_path(target_id)

    entities = sorted(
        data.get("entities", []),
        key=lambda item: str(item["entity_id"]),
    )

    raw = {
        "map_name": map_name,
        "player_start": list(data["player_start"]),
        "walls": _sorted_hexes(data["walls"]),
        "mud": _sorted_hexes(data["mud"]),
        "water_shallow": _sorted_hexes(data["water_shallow"]),
        "water_deep": _sorted_hexes(data["water_deep"]),
        "water_very_deep": _sorted_hexes(data["water_very_deep"]),
        "entities": [
            {
                "entity_id": str(item["entity_id"]),
                "entity_type": str(item["entity_type"]),
                "position": list(item["position"]),
            }
            for item in entities
        ],
    }

    with target_path.open("w", encoding="utf-8") as file:
        json.dump(raw, file, indent=4)

    if old_id is not None and old_id != target_id:
        old_path = _map_path(old_id)
        if old_path.exists():
            old_path.unlink()
        if old_was_default:
            set_default_map_id(target_id)

    return target_id, target_path


def delete_map_data(map_id):
    if map_id is None:
        raise ValueError("Current map has not been saved yet.")

    safe_id = _safe_map_id(map_id)
    path = _map_path(safe_id)
    if not path.exists():
        raise FileNotFoundError(f"Saved map not found: {safe_id}")

    was_default = get_default_map_id() == safe_id
    path.unlink()

    if was_default and DEFAULT_MAP_POINTER_PATH.exists():
        DEFAULT_MAP_POINTER_PATH.unlink()

    return path


def load_default_map_data():
    default_map_id = get_default_map_id()
    if default_map_id is None:
        return built_in_map_data()

    try:
        return load_map_data(default_map_id)
    except (OSError, json.JSONDecodeError):
        return built_in_map_data()