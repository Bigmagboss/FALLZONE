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

MAX_MOVE_RANGE = 100

MOVE_ENERGY_COST_PER_HEX = 1

MOVE_STEP_MS = 120

PLAYER_START = (
    10,
    5,
)


# --------------------------------------------------
# DEVELOPMENT LIMITS
# --------------------------------------------------

DEV_MIN_ENERGY = 0
DEV_MAX_ENERGY = 500

DEV_MIN_MOVE_RANGE = 1
DEV_MAX_MOVE_RANGE = 200

DEV_MIN_MOVE_STEP_MS = 20
DEV_MAX_MOVE_STEP_MS = 1000


# --------------------------------------------------
# TERRAIN COSTS
# --------------------------------------------------

MUD_MOVE_COST = 2

WATER_SHALLOW_MOVE_COST = 2

WATER_DEEP_MOVE_COST = 3

WATER_VERY_DEEP_MOVE_COST = 4


# --------------------------------------------------
# GENERAL COLOURS
# --------------------------------------------------

BACKGROUND = (
    18,
    18,
    20,
)

HEX_FILL = (
    35,
    36,
    40,
)

HEX_OUTLINE = (
    78,
    80,
    86,
)


# --------------------------------------------------
# PLAYER COLOURS
# --------------------------------------------------

PLAYER_FILL = (
    70,
    195,
    115,
)

PLAYER_OUTLINE = (
    180,
    255,
    205,
)


# --------------------------------------------------
# MUD COLOURS
# --------------------------------------------------

MUD_FILL = (
    92,
    65,
    38,
)

MUD_OUTLINE = (
    150,
    105,
    58,
)

MUD_OUTLINE_WIDTH = 2


# --------------------------------------------------
# WATER COLOURS
# --------------------------------------------------

WATER_SHALLOW_FILL = (
    50,
    105,
    135,
)

WATER_SHALLOW_OUTLINE = (
    95,
    175,
    205,
)


WATER_DEEP_FILL = (
    34,
    70,
    120,
)

WATER_DEEP_OUTLINE = (
    70,
    135,
    190,
)


WATER_VERY_DEEP_FILL = (
    18,
    38,
    82,
)

WATER_VERY_DEEP_OUTLINE = (
    55,
    95,
    155,
)

WATER_OUTLINE_WIDTH = 2


# --------------------------------------------------
# WALL COLOURS
# --------------------------------------------------

WALL_FILL = (
    0,
    0,
    0,
)

WALL_OUTLINE = (
    230,
    230,
    235,
)

WALL_OUTLINE_WIDTH = 3


# --------------------------------------------------
# MOVEMENT RANGE COLOURS
# --------------------------------------------------

RANGE_GLOW_SOFT = (
    55,
    115,
    165,
)

RANGE_GLOW = (
    120,
    210,
    255,
)


# --------------------------------------------------
# PATH PREVIEW COLOURS
# --------------------------------------------------

PATH_PREVIEW_GLOW = (
    125,
    95,
    35,
)

PATH_PREVIEW = (
    255,
    210,
    85,
)

PATH_NUMBER_COLOR = (
    20,
    20,
    22,
)


# --------------------------------------------------
# VALID / INVALID HOVER COLOURS
# --------------------------------------------------

HOVER_VALID_GLOW_SOFT = (
    55,
    125,
    80,
)

HOVER_VALID_OUTLINE = (
    130,
    255,
    175,
)

HOVER_INVALID_GLOW_SOFT = (
    130,
    55,
    55,
)

HOVER_INVALID_OUTLINE = (
    255,
    125,
    125,
)


# --------------------------------------------------
# HUD / EDITOR COLOURS
# --------------------------------------------------

TEXT_COLOR = (
    230,
    230,
    235,
)

SUBTEXT_COLOR = (
    165,
    170,
    180,
)

PANEL_COLOR = (
    27,
    28,
    32,
)

BUTTON_COLOR = (
    60,
    65,
    72,
)

BUTTON_HOVER_COLOR = (
    82,
    90,
    100,
)


# --------------------------------------------------
# MAP EDITOR COLOURS
# --------------------------------------------------

EDITOR_ACCENT = (
    255,
    190,
    70,
)

EDITOR_PLAYER_START = (
    110,
    255,
    165,
)