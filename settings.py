VERSION = "0.0002"


# --------------------------------------------------
# WINDOW
# --------------------------------------------------

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 760

PANEL_WIDTH = 300

PLAY_AREA_WIDTH = (
    SCREEN_WIDTH
    - PANEL_WIDTH
)

FPS = 60


# --------------------------------------------------
# HEX GRID
# --------------------------------------------------

HEX_SIZE = 20

GRID_COLUMNS = 28
GRID_ROWS = 20

GRID_ORIGIN_X = 40
GRID_ORIGIN_Y = 40


# --------------------------------------------------
# PLAYER
# --------------------------------------------------

MAX_HP = 100
MAX_ENERGY = 100

MAX_MOVE_RANGE = 3

PLAYER_START = (10, 5)

MOVE_ENERGY_COST_PER_HEX = 1



# --------------------------------------------------
# DEVELOPMENT TOOLS
# --------------------------------------------------

DEV_ENERGY_STEP = 10

DEV_MIN_ENERGY = 10
DEV_MAX_ENERGY = 500

DEV_MIN_MOVE_RANGE = 1
DEV_MAX_MOVE_RANGE = 100


# --------------------------------------------------
# COLORS
# --------------------------------------------------

BACKGROUND = (18, 18, 20)

HEX_FILL = (35, 36, 40)
HEX_OUTLINE = (78, 80, 86)

PLAYER_FILL = (70, 195, 115)
PLAYER_OUTLINE = (180, 255, 205)

WALL_FILL = (105, 83, 68)
WALL_OUTLINE = (175, 140, 105)

RANGE_FILL = (60, 120, 170)
RANGE_OUTLINE = (120, 205, 255)

TEXT_COLOR = (230, 230, 235)
SUBTEXT_COLOR = (165, 170, 180)

PANEL_COLOR = (27, 28, 32)

BUTTON_COLOR = (60, 65, 72)
BUTTON_HOVER_COLOR = (82, 90, 100)


# --------------------------------------------------
# MOVEMENT RANGE
# --------------------------------------------------

RANGE_GLOW_SOFT = (55, 115, 165)
RANGE_GLOW = (120, 210, 255)

HOVER_VALID_GLOW_SOFT = (55, 125, 80)
HOVER_INVALID_GLOW_SOFT = (130, 55, 55)

HOVER_VALID_OUTLINE = (130, 255, 175)
HOVER_INVALID_OUTLINE = (255, 125, 125)