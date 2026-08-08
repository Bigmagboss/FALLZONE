import pygame



# --------------------------------------------------
# FALLZONE - Version 0.0001
# --------------------------------------------------


VERSION = "0.0001"


CELL_SIZE = 48
GRID_COLUMNS = 12
GRID_ROWS = 9
PANEL_WIDTH = 300

SCREEN_WIDTH = GRID_COLUMNS * CELL_SIZE + PANEL_WIDTH
SCREEN_HEIGHT = GRID_ROWS * CELL_SIZE

FPS = 60

MAX_ENERGY = 10
MAX_HP = 100


BACKGROUND = (20, 20, 20)
GRID_BACKGROUND = (35, 35, 35)
GRID_LINE = (80, 80, 80)

PLAYER_COLOR = (80, 200, 120)

PANEL_COLOR = (28, 28, 32)
TEXT_COLOR = (230, 230, 230)
WARNING_COLOR = (230, 170, 80)



def try_move(dx, dy):
    """Attempt to move one grid cell."""

    global player_x
    global player_y
    global player_energy
    global status_message

    if player_energy <= 0:
        status_message = "Not enough energy."
        return

    new_x = player_x + dx
    new_y = player_y + dy

    if not (
        0 <= new_x < GRID_COLUMNS
        and 0 <= new_y < GRID_ROWS
    ):
        status_message = "Movement blocked by map boundary."
        return

    player_x = new_x
    player_y = new_y

    player_energy -= 1

    status_message = (
        f"Moved to ({player_x}, {player_y}). Energy -1."
    )


pygame.init()


screen = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT)
)

pygame.display.set_caption(
    f"FALLZONE v{VERSION}"
)

clock = pygame.time.Clock()

font = pygame.font.Font(None, 30)
small_font = pygame.font.Font(None, 24)



player_x = 2
player_y = 2

player_hp = MAX_HP
player_energy = MAX_ENERGY

status_message = "Use WASD or arrow keys to move."


running = True


while running:

    # ----------------------------------------------
    # INPUT
    # ----------------------------------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key in (
                pygame.K_LEFT,
                pygame.K_a,
            ):
                try_move(-1, 0)

            elif event.key in (
                pygame.K_RIGHT,
                pygame.K_d,
            ):
                try_move(1, 0)

            elif event.key in (
                pygame.K_UP,
                pygame.K_w,
            ):
                try_move(0, -1)

            elif event.key in (
                pygame.K_DOWN,
                pygame.K_s,
            ):
                try_move(0, 1)


    # ----------------------------------------------
    # DRAW BACKGROUND
    # ----------------------------------------------

    screen.fill(BACKGROUND)


    grid_width = GRID_COLUMNS * CELL_SIZE
    grid_height = GRID_ROWS * CELL_SIZE


    pygame.draw.rect(
        screen,
        GRID_BACKGROUND,
        pygame.Rect(
            0,
            0,
            grid_width,
            grid_height,
        ),
    )


    # ----------------------------------------------
    # DRAW GRID
    # ----------------------------------------------

    for row in range(GRID_ROWS):

        for column in range(GRID_COLUMNS):

            cell = pygame.Rect(
                column * CELL_SIZE,
                row * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE,
            )

            pygame.draw.rect(
                screen,
                GRID_LINE,
                cell,
                1,
            )


    # ----------------------------------------------
    # DRAW PLAYER
    # ----------------------------------------------

    player_rect = pygame.Rect(
        player_x * CELL_SIZE + 6,
        player_y * CELL_SIZE + 6,
        CELL_SIZE - 12,
        CELL_SIZE - 12,
    )

    pygame.draw.rect(
        screen,
        PLAYER_COLOR,
        player_rect,
    )


    # ----------------------------------------------
    # DRAW INFORMATION PANEL
    # ----------------------------------------------

    panel_x = grid_width

    panel_rect = pygame.Rect(
        panel_x,
        0,
        PANEL_WIDTH,
        SCREEN_HEIGHT,
    )

    pygame.draw.rect(
        screen,
        PANEL_COLOR,
        panel_rect,
    )


    title = font.render(
        f"FALLZONE v{VERSION}",
        True,
        TEXT_COLOR,
    )

    hp_text = font.render(
        f"HP: {player_hp} / {MAX_HP}",
        True,
        TEXT_COLOR,
    )

    energy_text = font.render(
        f"ENERGY: {player_energy} / {MAX_ENERGY}",
        True,
        TEXT_COLOR,
    )

    position_text = font.render(
        f"POSITION: ({player_x}, {player_y})",
        True,
        TEXT_COLOR,
    )

    status_text = small_font.render(
        status_message,
        True,
        WARNING_COLOR,
    )


    screen.blit(
        title,
        (panel_x + 20, 30),
    )

    screen.blit(
        hp_text,
        (panel_x + 20, 90),
    )

    screen.blit(
        energy_text,
        (panel_x + 20, 130),
    )

    screen.blit(
        position_text,
        (panel_x + 20, 170),
    )

    screen.blit(
        status_text,
        (panel_x + 20, 230),
    )



    pygame.display.flip()

    clock.tick(FPS)



pygame.quit()