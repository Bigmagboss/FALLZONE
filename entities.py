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
    max_movement: int
    max_energy: int
    energy_per_move: int


ENTITY_TYPES = {
    "enemy": EntityType(
        key="enemy",
        label="ENEMY",
        short_label="E",
        blocks_movement=True,
        fill=cfg.ENEMY_FILL,
        outline=cfg.ENEMY_OUTLINE,
        max_movement=cfg.ENEMY_MAX_MOVE_RANGE,
        max_energy=cfg.ENEMY_MAX_ENERGY,
        energy_per_move=cfg.ENEMY_ENERGY_COST_PER_MOVE,
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
    movement_remaining: int = 0
    energy: int = 0

    @property
    def definition(self):
        return ENTITY_TYPES[self.entity_type]

    @property
    def blocks_movement(self):
        return self.definition.blocks_movement

    @property
    def max_movement(self):
        return self.definition.max_movement

    @property
    def max_energy(self):
        return self.definition.max_energy

    def reset_runtime_resources(self):
        self.movement_remaining = self.max_movement
        self.energy = self.max_energy

    def reset_turn_movement(self):
        self.movement_remaining = self.max_movement

    def can_move(self, movement_cost):
        if movement_cost < 1:
            return False
        energy_cost = movement_cost * self.definition.energy_per_move
        return (
            movement_cost <= self.movement_remaining
            and energy_cost <= self.energy
        )

    def move_to(self, destination, movement_cost):
        if not self.can_move(movement_cost):
            return False

        energy_cost = movement_cost * self.definition.energy_per_move
        self.position = tuple(destination)
        self.movement_remaining -= movement_cost
        self.energy -= energy_cost
        return True


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

        entity = Entity(
            entity_id=str(spawn["entity_id"]),
            entity_type=entity_type,
            position=tuple(spawn["position"]),
        )
        entity.reset_runtime_resources()
        entities.append(entity)

    return entities


def find_entity_at(entities, position):
    for entity in entities:
        if entity.position == position:
            return entity
    return None


def blocked_entity_positions(entities, exclude=None):
    excluded_id = None if exclude is None else exclude.entity_id
    return {
        entity.position
        for entity in entities
        if entity.blocks_movement and entity.entity_id != excluded_id
    }