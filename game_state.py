import settings as cfg


class GameState:

    def __init__(
        self,
    ):

        # --------------------------------------------------
        # SESSION SETTINGS
        # --------------------------------------------------

        self.session_max_energy = (
            cfg.MAX_ENERGY
        )

        self.session_max_move_range = (
            cfg.MAX_MOVE_RANGE
        )

        self.session_move_step_ms = (
            cfg.MOVE_STEP_MS
        )

        self.session_player_start = (
            cfg.PLAYER_START
        )


        # --------------------------------------------------
        # TURN STATE
        # --------------------------------------------------

        self.turn_number = 1


        # --------------------------------------------------
        # DEVELOPMENT DISPLAY STATE
        # --------------------------------------------------

        self.dev_show_path_numbers = (
            False
        )


        # --------------------------------------------------
        # INITIAL PLAYER
        # --------------------------------------------------

        self.reset_player()


    # --------------------------------------------------
    # PLAYER POSITION
    # --------------------------------------------------

    @property
    def player_position(
        self,
    ):

        return (
            self.player_q,
            self.player_r,
        )


    # --------------------------------------------------
    # CHECK MOVEMENT COST
    # --------------------------------------------------

    def can_move(
        self,
        movement_cost,
    ):

        if movement_cost < 1:

            return False


        energy_cost = (
            movement_cost
            * cfg.MOVE_ENERGY_COST_PER_HEX
        )


        return (
            movement_cost
            <= self.movement_remaining

            and

            energy_cost
            <= self.player_energy
        )


    # --------------------------------------------------
    # MOVE ONE ANIMATED STEP
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
            f"Entered {destination}; "
            f"cost {movement_cost}."
        )


        return True


    # --------------------------------------------------
    # START NEW GAME FROM CURRENT EDITED MAP
    # --------------------------------------------------

    def start_new_game_session(
        self,
        player_start,
    ):

        self.session_player_start = (
            tuple(
                player_start
            )
        )


        self.turn_number = 1


        self.reset_player()


        self.status_message = (
            "Game session started "
            "from edited map."
        )


    # --------------------------------------------------
    # END TURN
    # --------------------------------------------------

    def end_turn(
        self,
    ):

        self.turn_number += 1


        self.movement_remaining = (
            self.session_max_move_range
        )


        self.status_message = (
            f"Turn {self.turn_number} started."
        )


    # --------------------------------------------------
    # RESET TURN - DEV
    # --------------------------------------------------

    def reset_turn(
        self,
    ):

        self.movement_remaining = (
            self.session_max_move_range
        )


        self.status_message = (
            "DEV: movement budget reset."
        )


    # --------------------------------------------------
    # RESET PLAYER - DEV
    # --------------------------------------------------

    def reset_player(
        self,
    ):

        (
            self.player_q,
            self.player_r,
        ) = self.session_player_start


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
    # SET ENERGY
    # --------------------------------------------------

    def set_session_energy(
        self,
        value,
    ):

        value = max(
            cfg.DEV_MIN_ENERGY,
            min(
                int(
                    value
                ),
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
    # SET MOVEMENT
    # --------------------------------------------------

    def set_session_move_range(
        self,
        value,
    ):

        value = max(
            cfg.DEV_MIN_MOVE_RANGE,
            min(
                int(
                    value
                ),
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


    # --------------------------------------------------
    # SET MOVEMENT ANIMATION SPEED
    # --------------------------------------------------

    def set_session_move_step_ms(
        self,
        value,
    ):

        value = max(
            cfg.DEV_MIN_MOVE_STEP_MS,
            min(
                int(
                    value
                ),
                cfg.DEV_MAX_MOVE_STEP_MS,
            ),
        )


        self.session_move_step_ms = (
            value
        )


        self.status_message = (
            "Movement speed set to "
            f"{value} ms."
        )


        return value


    # --------------------------------------------------
    # TOGGLE PATH NUMBERS
    # --------------------------------------------------

    def toggle_path_numbers(
        self,
    ):

        self.dev_show_path_numbers = (
            not self.dev_show_path_numbers
        )


        if self.dev_show_path_numbers:

            state_text = "ON"

        else:

            state_text = "OFF"


        self.status_message = (
            "DEV: path numbers "
            f"{state_text}."
        )