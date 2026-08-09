import settings as cfg


class GameState:

    def __init__(self):

        self.session_max_energy = (
            cfg.MAX_ENERGY
        )

        self.session_max_move_range = (
            cfg.MAX_MOVE_RANGE
        )

        self.reset_player()


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
            f"Moved {movement_cost} hex(es)."
        )

        return True


    # --------------------------------------------------
    # DEVELOPMENT RESET CONTROLS
    # --------------------------------------------------

    def reset_turn(self):

        self.movement_remaining = (
            self.session_max_move_range
        )

        self.status_message = (
            "Movement budget reset."
        )


    def reset_player(self):

        self.player_q, self.player_r = (
            cfg.PLAYER_START
        )

        self.player_hp = (
            cfg.MAX_HP
        )

        self.player_energy = (
            self.session_max_energy
        )

        self.movement_remaining = (
            self.session_max_move_range
        )

        self.status_message = (
            "Player reset."
        )


    # --------------------------------------------------
    # DEVELOPMENT ENERGY CONTROL
    # --------------------------------------------------

    def adjust_session_energy(
        self,
        amount,
    ):
        old_max = (
            self.session_max_energy
        )

        energy_spent = max(
            0,
            old_max
            - self.player_energy,
        )

        new_max = (
            old_max
            + amount
        )

        new_max = max(
            cfg.DEV_MIN_ENERGY,
            min(
                new_max,
                cfg.DEV_MAX_ENERGY,
            ),
        )

        self.session_max_energy = (
            new_max
        )

        self.player_energy = max(
            0,
            new_max
            - energy_spent,
        )

        self.status_message = (
            f"Session energy set to "
            f"{new_max}."
        )


    # --------------------------------------------------
    # DEVELOPMENT MOVEMENT CONTROL
    # --------------------------------------------------

    def adjust_session_move_range(
        self,
        amount,
    ):
        old_max = (
            self.session_max_move_range
        )

        movement_spent = max(
            0,
            old_max
            - self.movement_remaining,
        )

        new_max = (
            old_max
            + amount
        )

        new_max = max(
            cfg.DEV_MIN_MOVE_RANGE,
            min(
                new_max,
                cfg.DEV_MAX_MOVE_RANGE,
            ),
        )

        self.session_max_move_range = (
            new_max
        )

        self.movement_remaining = max(
            0,
            new_max
            - movement_spent,
        )

        self.status_message = (
            f"Session movement set to "
            f"{new_max}."
        )