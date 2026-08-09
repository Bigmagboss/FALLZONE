import settings as cfg


class GameState:

    def __init__(self):
        self.reset()


    @property
    def player_position(self):
        return (
            self.player_q,
            self.player_r,
        )


    def can_move(
        self,
        movement_cost,
    ):
        enough_movement = (
            movement_cost
            <= self.movement_remaining
        )

        energy_cost = (
            movement_cost
            * cfg.MOVE_ENERGY_COST_PER_HEX
        )

        enough_energy = (
            energy_cost
            <= self.player_energy
        )

        return (
            movement_cost >= 1
            and
            enough_movement
            and
            enough_energy
        )


    def move_player_to(
        self,
        destination,
        movement_cost,
    ):
        if not self.can_move(
            movement_cost
        ):
            return False

        energy_cost = (
            movement_cost
            * cfg.MOVE_ENERGY_COST_PER_HEX
        )

        self.player_q, self.player_r = (
            destination
        )

        self.movement_remaining -= (
            movement_cost
        )

        self.player_energy -= (
            energy_cost
        )

        self.status_message = (
            f"Moved {movement_cost} hex(es) "
            f"to {destination}."
        )

        return True


    def reset(self):
        self.player_q, self.player_r = (
            cfg.PLAYER_START
        )

        self.player_hp = cfg.MAX_HP
        self.player_energy = cfg.MAX_ENERGY

        self.movement_remaining = (
            cfg.MAX_MOVE_RANGE
        )

        self.status_message = (
            "FALLZONE v0.0002 ready."
        )