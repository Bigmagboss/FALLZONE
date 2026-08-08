# FALLZONE v0.0001 Test Plan

## Test Objective

Verify that FALLZONE v0.0001 meets the defined requirements for the first playable grid-movement prototype.

## Test Environment

- Operating System: Windows
- Python: 3.14.6
- pygame-ce: 2.5.7
- Test Type: Manual functional testing
- Build: v0.0001

## Requirements

| Requirement ID | Requirement |
|---|---|
| FZ-REQ-001 | The game launches successfully. |
| FZ-REQ-002 | A visible square grid is displayed. |
| FZ-REQ-003 | The player is visible on the grid. |
| FZ-REQ-004 | The player starts with 100 HP. |
| FZ-REQ-005 | The player starts with 10 energy. |
| FZ-REQ-006 | WASD and arrow keys move the player exactly on grid cell. |
| FZ-REQ-007 | Each successful movement cost exactly 1 energy. |
| FZ-REQ-008 | The player cannot move outside the map boundaries. |
| FZ-REQ-009 | Blocked boundary movement does not consume energy. |
| FZ-REQ-010 | The player cannot move when energy reaches 0. |
| FZ-REQ-011 | Player energy can never become negative. |
| FZ-REQ-012 | HP, energy and player coordinates are visible on screen. |
| FZ-REQ-013 | Closing the game window exits the program cleanly. |

## Test Cases

### FZ-TC-001 - Game Launch

**Requirement:** FZ-REQ-001

**Purpose:** Verify that FALLZONE launches successfully.

**Preconditions:**
- FALLZONE virtual environment is active.
- pygame-ce is installed.
- The terminal is located in the FALLZONE project directory.

**Test Steps:**
1. Open the VS Code terminal.
2. Run `python main.py`.
3. Observe the application.

**Expected Result:**
- A FALLZONE game windows opens.
- No Python traceback is displayed.
- The game remains running until the user closes it.

### FZ-TC-002 - Grid Display

**Requirement:** FZ-REQ-002

**Purpose:** Verify that the game grid is visible.

**Preconditions:**
- FALLZONE is running.

**Test Steps:**
1. Launch FALLZONE.
2. Observe the main game area.

**Expected Result:**
- A square grid is visible.
- Grid cells can be visually distinguished from each other.

### FZ-TC-003 - Player Display

**Requirement:** FZ-REQ-003

**Purpose:** Verify that the player is visible on the grid.

**Preconditions:**
- FALLZONE is running.

**Test Steps:**
1. Launch FALLZONE
2. Observe the grid.

**Expected Result:**
- A player rectangle is visible.
- The player occupies one grid cell.

### FZ-TC-004 - Initial Player HP

**Requirement:** FZ-REQ-004

**Purpose:** Verify the player's starting HP.

**Preconditions:**
- Start a fresh FALLZONE session.

**Test Steps:**
1. Launch FALLZONE.
2. Locate the HP display.
3. Record the displayed HP value.

**Expected Result:**
- HP displays `100 / 100`.

### FZ-TC-005 - Initial Player Energy

**Requirement:** FZ-REQ-005

**Purpose:** Verify the player's starting energy.

**Preconditions:**
- Start a fresh FALLZONE session.

**Test Steps:**
1. Launch FALLZONE.
2. Locate the energy display.
3. Record the display energy value.

**Expected Result:**
- Energy displays `10 / 10`.

### FZ-TC-006 - Move Right

**Requirement:** FZ-REQ-006

**Purpose:** Verify that pressing Right moves the player exactly one grid cell.

**Preconditions:**
- FALLZONE is running.
- Player is not standing against the right map boundary.
- Player has at least 1 energy.

**Test Steps:**
1. Record the player's current coordinates.
2. Press the Right Arrow key once.
3. Record the new coordinates.

**Expected Result:**
- Player X coordinate increases by exactly 1.
- Player Y coordinate remains unchanged.

### FZ-TC-007 - Move Left

**Requirement:** FZ-REQ-006

**Purpose:** Verify that pressing Left moves the player exactly one grid cell.

**Preconditions:**
- FALLZONE is running.
- Player is not standing against the left map boundary.
- Player has at least 1 energy.

**Test Steps:**
1. Record the player's current coordinates.
2. Press the Left Arrow key once.
3. Record the new coordinates.

**Expected Result:**
- Player X coordinate decreases by exactly 1.
- Player Y coordinate remains unchanged.

### FZ-TC-008 - Move Up

**Requirement:** FZ-REQ-006

**Purpose:** Verift that pressing Up moves the player exactly one grid cell.

**Preconditions:**
- FALLZONE is running.
- Player is not standing against the upper map boundary.
- Player has at least 1 energy.

**Test Steps:**
1. Record the player's current coordinates.
2. Press the Up Arrow key once.
3. Record the new coordinates.

**Expected Result:**
- Player Y coordinate decreases by exactly 1.
- Player X coordinate remains unchanged.

### FZ-TC-009 - Move Down

**Requirement:** FZ-REQ-006

**Purpose:** Verify that pressing Down moves the player exactly one grid cell.

**Preconditions:**
- FALLZONE is running.
- Player is not standing against the lower map boundary.
- Player has at least 1 energy.


**Test Steps:**
1. Record the player's current coordinates.
2. Press the Down Arrow key once.
3. Record the new coordinates.

**Expected Result:**
- Player Y coordinate increases by exactly 1.
- Player X coordinate remains unchanged.

### FZ-RC-010 - WASD Movement

**Requirement:** FZ-REQ-006

**Purpose:** Verify that W, A, S and D provide the expected movement controls.

**Preconditions:**
- FALLZONE is running.
- Player is away from map boundaries.
- Player has sufficient energy.

**Test Steps:**
1. Press `W` once.
2. Restart FALLZONE.
3. Press `A` once.
4. Restart FALLZONE.
5. Press `S` once.
6. Restart FALLZONE.
7. Press `D` once.

**Expected Result:**
- W moves one cell up.
- A moves one cell left.
- S moves one cell down.
- D moves one cell right.

### FZ-TC-011 - Movement Energy Cost

**Requirement:** FZ-REQ-007

**Purpose:** Verify that one successful movement consumes exactly 1 energy.

**Preconditions:**
- Start a fresh FALLZONE session.
- Energy displays `10/10`.
- Player is able to move.

**Test Steps:**
1. Confirm energy is 10.
2. Press Right once.
3. Record the new energy value.

**Expected Result:**
- Player moves one cell.
- Energy changes from 10 to 9.

### FZ-TC-012 - Left Map Boundary

**Requirement:** FZ-REQ-008

**Purpose:** Verify that the player cannot leave the map through the left boundary.

**Preconditions:**
- FALLZONE is running.
- Player has sufficient energy.

**Test Steps:**
1. Move the player until the X coordinate reaches 0.
2. Confirm the player is at X = 0.
3. Press Left once more.
4. Record the player's coordinates.

**Expected Result:**
- Player remains at X = 0.
- Player does not move outside the grid.

### FZ-TC-013 - Blocked Boundary Movement Energy

**Requirement:** FZ-REQ-009

**Purpose:** Verift that an unsuccesful boundary movement does not consume energy.

**Preconditions:**
- Player is stnading at a map boundary.
- Player has at least 1 energy remaining.

**Test Steps:**
1. Position the player at X = 0.
2. Record the current energy value.
3. Press Left once.
4. Record the energy value again.

**Expected Result:**
- Player does not move.
- Energy remains unchanged.

### FZ-TC-014 - All Map Boundaries

**Requirement:** FZ-REQ-008

**Purpose:** Verify that all four map boundaries prevent movement outside the grid.

**Test Steps:**
1. Test the left boundary.
2. Restart FALLZONE.
3. Test the right boundary.
4. Restart FALLZONE.
5. Test the upper boundary.
6. Restart FALLZONE.
7. Test the lower boundary.

**Expected Result:**
- Left boundary blocks left movement.
- Right boundary blocks right movement.
- Upper boundary blocks upward movement.
- Lower boundary blocks downward movement.

### FZ-TC-015 - Energy Reaches Zero

**Requirement:** FZ-REQ-010

**Purpose:** Verify behaviour when all player energy is consumed.

**Preconditions:**
- Start a fresh FALLZONE session.
- Energy is 10.

**Test Steps:**
1. Perform 10 successful movements.
2. Observe the energy display.

**Expected Result:**
- Energy decreases once per valid movement.
- After 10 successful movements, energy displays `0 / 10`.

### FZ-TC-016 - Movement at Zero Energy

**Requirement:** FZ-REQ-010

**Purpose:** Verify that the player cannot move when energy reaches zero.

**Preconditions:**
- FALLZONE is running.
- Player energy is 0.
- Player is not standing against a map boundary.

**Test Steps:**
1. Record the player's coordinates.
2. Press a movement key once.
3. Record the coordinates again.

**Expected Result:**
- Player coordinates remain unchanged.
- Player does not move.

### FZ-TC-017 - Energy Cannot Become Negative

**Requirement:** FZ-REQ-011

**Purpose:** Verify that repeated movement attempts cannot reduce energy below zero.

**Preconditions:**
- Player energy is 0.

**Test Steps:**
1. Press movement keys 10 additional times.
2. Observe the energy display.

**Expected Result:**
- Energy remains at `0 / 10`.
- Energy never displays a negative number.

### FZ-TC-018 - Player Information Display

**Requirement:** FZ-REQ-012

**Purpose:** Verify that important player information is visible.

**Preconditions:**
- FALLZONE is running.

**Test Steps:**
1. Observe the information panel.
2. Locate HP.
3. Locate energy.
4. Locate player coordinates.
5. Perform one successful movement.
6. Observe energy and coordinates again.

**Expected Result:**
- HP is visible.
- Energy is visible.
- Coordinates are visible.
- Energy updates after movement.
- Coordinates update after movement.

### FZ-TC-019 - Clean Window Exit

**Requirement:** FZ-REQ-013

**Purpose:** Verify that FALLZONE exits cleanly when the window is closed.

**Preconditions:**
- FALLZONE is running.

**Test Steps:**
1. Click the X button on the game window.
2. Observe the game window.
3. Observe the VS Code terminal.

**Expected Result:**
- The game window closes.
- The Python process ends.
- No traceback or crash error appeats.
- Control returns to the PowerShell prompt.