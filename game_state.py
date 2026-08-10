import settings as cfg


class GameState:

    def __init__(self):

        # --------------------------------------------------
        # SESSION SETTINGS
        # --------------------------------------------------

        self.session_max_energy = (
            cfg.MAX_ENERGY
        )

        self.session_max_move_range = (
            cfg.MAX_MOVE_RANGE
        )


        # --------------------------------------------------
        # TURN STATE
        # --------------------------------------------------

        self.turn_number = 1


        # --------------------------------------------------
        # INITIAL PLAYER STATE
        # --------------------------------------------------

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
    # CHECK WHETHER MOVEMENT CAN BE PAID FOR
    # --------------------------------------------------

    def can_move(
        self,
        movement_cost,
    ):

        if movement_cost < 1:
            return False


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
    # END GAMEPLAY TURN
    # --------------------------------------------------

    def end_turn(self):

        self.turn_number += 1


        self.movement_remaining = (
            self.session_max_move_range
        )


        # Energy deliberately does NOT refill.
        #
        # Later this method can also trigger:
        #
        # enemy actions
        # status effects
        # cooldowns
        # environmental effects
        # start-of-turn logic

        self.status_message = (
            f"Turn {self.turn_number} started."
        )


    # --------------------------------------------------
    # RESET MOVEMENT ONLY - DEV TOOL
    # --------------------------------------------------

    def reset_turn(self):

        self.movement_remaining = (
            self.session_max_move_range
        )


        self.status_message = (
            "DEV: movement budget reset."
        )


    # --------------------------------------------------
    # RESET PLAYER - DEV TOOL
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
    # DEVELOPER ENERGY OVERRIDE
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
    # DEVELOPER MOVEMENT OVERRIDE
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