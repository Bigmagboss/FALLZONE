from dataclasses import dataclass

import settings as cfg


@dataclass(frozen=True)
class EntityType:
    key: str
    label: str
    short_label: str
    blocks_movement: bool
    fill: tuple
    outline: tuple


ENTITY_TYPES = {
    "enemy": EntityType(
        key="enemy",
        label="ENEMY",
        short_label="E",
        blocks_movement=True,
        fill=cfg.ENEMY_FILL,
        outline=cfg.ENEMY_OUTLINE,
    ),
}

EDITOR_ENTITY_ORDER = (
    "enemy",
)

ENTITY_BRUSH_PREFIX = "entity:"


@dataclass
class Entity:
    entity_id: str
    entity_type: str
    position: tuple

    @property
    def definition(self):
        return ENTITY_TYPES[self.entity_type]

    @property
    def blocks_movement(self):
        return self.definition.blocks_movement


def make_entity_brush(entity_type):
    if entity_type not in ENTITY_TYPES:
        raise ValueError(f"Unknown entity type: {entity_type}")
    return f"{ENTITY_BRUSH_PREFIX}{entity_type}"


def entity_type_from_brush(brush):
    if not brush.startswith(ENTITY_BRUSH_PREFIX):
        return None
    entity_type = brush[len(ENTITY_BRUSH_PREFIX):]
    return entity_type if entity_type in ENTITY_TYPES else None


def create_entities_from_spawns(spawns):
    entities = []
    for spawn in spawns:
        entity_type = spawn.get("entity_type")
        if entity_type not in ENTITY_TYPES:
            continue
        entities.append(
            Entity(
                entity_id=str(spawn["entity_id"]),
                entity_type=entity_type,
                position=tuple(spawn["position"]),
            )
        )
    return entities


def find_entity_at(entities, position):
    for entity in entities:
        if entity.position == position:
            return entity
    return None


def blocked_entity_positions(entities):
    return {
        entity.position
        for entity in entities
        if entity.blocks_movement
    }