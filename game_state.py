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

    def move_player_to(
            self,
            destination,
    ):
        self.player_q, self.player_r = (
            destination
        )

        self.status_message = (
            f"Moved to {destination}."
        )


    def reset(self):
        self.player_q, self.player_r = (
            cfg.PLAYER_START
        )

        self.player_hp = cfg.MAX_HP
        self.player_energy = cfg.MAX_ENERGY

        self.status_message = (
            "FALLZONE v0.0002 ready."
        )