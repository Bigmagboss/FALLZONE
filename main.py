import pygame

import settings as cfg

from game_state import GameState

from hex_grid import (
    axial_to_pixel,
    hex_corners,
    offset_to_axial,
)

pygame.init()

screen = pygame.display.set_mode(
    (
        cfg.SCREEN_WIDTH,
        cfg.SCREEN_HEIGHT,
    )
)

pygame.display.set_caption(
    f"FALLZONE v{cfg.VERSION}"
)

clock = pygame.time.Clock()

state = GameState()

font = pygame.font.Font(
    None,
    30,
)

small_font = pygame.font.Font(
    None,
    22,
)

running = True


while running:

    # --------------------------------------------------
    # EVENTS
    # --------------------------------------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False


    # --------------------------------------------------
    # DRAW BACKGROUND
    # --------------------------------------------------

    screen.fill(
        cfg.BACKGROUND
    )


    # --------------------------------------------------
    # DRAW HEX GRID
    # --------------------------------------------------

    for column in range(
        cfg.GRID_COLUMNS
    ):

        for row in range(
            cfg.GRID_ROWS
        ):

            hex_position = offset_to_axial(
                column,
                row,
            )

            center = axial_to_pixel(
                hex_position
            )

            points = hex_corners(
                center
            )

            pygame.draw.polygon(
                screen,
                cfg.HEX_FILL,
                points,
            )

            pygame.draw.polygon(
                screen,
                cfg.HEX_OUTLINE,
                points,
                1,
            )


    # --------------------------------------------------
    # DRAW PLAYER
    # --------------------------------------------------

    player_center = axial_to_pixel(
        state.player_position
    )

    player_points = hex_corners(
        player_center,
        cfg.HEX_SIZE * 0.55,
    )

    pygame.draw.polygon(
        screen,
        cfg.PLAYER_FILL,
        player_points,
    )

    pygame.draw.polygon(
        screen,
        cfg.PLAYER_OUTLINE,
        player_points,
        2,
    )


    # --------------------------------------------------
    # DRAW INFORMATION PANEL
    # --------------------------------------------------

    panel_x = (
        cfg.SCREEN_WIDTH
        - cfg.PANEL_WIDTH
    )

    panel_rect = pygame.Rect(
        panel_x,
        0,
        cfg.PANEL_WIDTH,
        cfg.SCREEN_HEIGHT,
    )

    pygame.draw.rect(
        screen,
        cfg.PANEL_COLOR,
        panel_rect,
    )


    # --------------------------------------------------
    # CREATE HUD TEXT
    # --------------------------------------------------

    title_text = font.render(
        f"FALLZONE v{cfg.VERSION}",
        True,
        cfg.TEXT_COLOR,
    )

    hp_text = font.render(
        (
            f"HP: "
            f"{state.player_hp} "
            f"/ {cfg.MAX_HP}"
        ),
        True,
        cfg.TEXT_COLOR,
    )

    energy_text = font.render(
        (
            f"ENERGY: "
            f"{state.player_energy} "
            f"/ {cfg.MAX_ENERGY}"
        ),
        True,
        cfg.TEXT_COLOR,
    )

    position_text = font.render(
        (
            f"HEX: "
            f"{state.player_position}"
        ),
        True,
        cfg.TEXT_COLOR,
    )

    debug_title = small_font.render(
        "DEVELOPMENT BUILD",
        True,
        cfg.SUBTEXT_COLOR,
    )


    # --------------------------------------------------
    # DRAW HUD TEXT
    # --------------------------------------------------

    screen.blit(
        title_text,
        (
            panel_x + 24,
            32,
        ),
    )

    screen.blit(
        hp_text,
        (
            panel_x + 24,
            90,
        ),
    )

    screen.blit(
        energy_text,
        (
            panel_x + 24,
            130,
        ),
    )

    screen.blit(
        position_text,
        (
            panel_x + 24,
            170,
        ),
    )

    screen.blit(
        debug_title,
        (
            panel_x + 24,
            230,
        ),
    )


    # --------------------------------------------------
    # FINISH FRAME
    # --------------------------------------------------

    pygame.display.flip()

    clock.tick(
        cfg.FPS
    )


pygame.quit()