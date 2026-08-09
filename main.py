import pygame

import settings as cfg

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

running = True


while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False


    screen.fill(
        cfg.BACKGROUND
    )


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


    pygame.display.flip()

    clock.tick(
        cfg.FPS
    )


pygame.quit()