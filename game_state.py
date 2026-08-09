import settings as cfg


class GameState:

    def __init__(self):

        # These begin with the normal game defaults,
        # but developer controls may change them
        # temporarily during this running session.

        self.session_max_energy = (
            cfg.MAX_ENERGY
        )

        self.session_max_move_range = (
            cfg.MAX_MOVE_RANGE
        )

        self.reset_player()


    # --------------------------------------------------
    # PLAYER POSITION
    # --------------------------------------------------

    @property
    def player_position(self):
        return (
            self.player_q,
            self.player_r,
        )


    # --------------------------------------------------
    # MOVEMENT VALIDATION
    # --------------------------------------------------

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


    # --------------------------------------------------
    # MOVE PLAYER
    # --------------------------------------------------

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
    # RESET CURRENT MOVEMENT BUDGET
    # --------------------------------------------------

    def reset_turn(self):

        self.movement_remaining = (
            self.session_max_move_range
        )

        self.status_message = (
            "Movement budget reset."
        )


    # --------------------------------------------------
    # RESET PLAYER
    # --------------------------------------------------

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
    # SET SESSION ENERGY
    # --------------------------------------------------

    def set_session_energy(
        self,
        value,
    ):

        value = int(
            value
        )

        value = max(
            cfg.DEV_MIN_ENERGY,
            min(
                value,
                cfg.DEV_MAX_ENERGY,
            ),
        )

        # Developer override:
        # replace both the session maximum
        # and current energy.

        self.session_max_energy = (
            value
        )

        self.player_energy = (
            value
        )

        self.status_message = (
            f"Energy set to {value}."
        )

        return value


    # --------------------------------------------------
    # SET SESSION MOVEMENT
    # --------------------------------------------------

    def set_session_move_range(
        self,
        value,
    ):

        value = int(
            value
        )

        value = max(
            cfg.DEV_MIN_MOVE_RANGE,
            min(
                value,
                cfg.DEV_MAX_MOVE_RANGE,
            ),
        )

        # Developer override:
        # replace both maximum movement
        # and movement remaining.

        self.session_max_move_range = (
            value
        )

        self.movement_remaining = (
            value
        )

        self.status_message = (
            f"Movement set to {value}."
        )

        return value