# FALLZONE v0.0001 Test Results

## Test Session

- Build: v0.0001
- Tester: Raimonds Klivis
- Test Type: Manual functional testing
- Operating System: Windows
- Python: 3.14.6
- pygame-ce: 2.5.7

## Result Definitions

- **PASS** - Actual result matches the expected result.
- **FAIL** - Actual result does not match the expected result.
- **BLOCKED** - The test cannot currently be completed because another problem prevents execution.
- **NOT RUN** - The test has not yet been executed.

## Test Summary

| Test Case | Status | Actual Result | Notes |
|---|---|---|---|
| FZ-TC-001 | PASS | Game window opened successfully and remained running. No traceback displayed. | |
| FZ-TC-002 | PASS | Square grid displayed correctly and individual grid cells were visible. | No visual issue observed. |
| FZ-TC-003 | PASS | Player rectanlge was visible within one grid cell. | |
| FZ-TC-004 | PASS | HP displayed as 100 / 100 at launch. | |
| FZ-TC-005 | PASS | Energy displayed as 10 / 10 at launch. | |
| FZ-TC-006 | PASS | Position changed from (2, 2) to (3, 2).  | X increased by exactly 1; Y unchanged. |
| FZ-TC-007 | PASS | Position changed from (2, 2) to (1, 2). | x decreased by exactly 1; Y unchanged. |
| FZ-TC-008 | PASS | Position changed from (2, 2) to (2, 1). | y decreased by exactly 1; x unchanged. |
| FZ-TC-009 | PASS | Position changed from (2, 2) to (2, 3). | y increased by exactly 1; x unchanged. |
| FZ-TC-010 | PASS | W moves one grid up, A moves one grid left, D moves one grid right, S moves one grid down. | |
| FZ-TC-011 | PASS | Energy changes from 10 to 9 when moved to right. | |
| FZ-TC-012 | PASS | Previous position was (0, 2) when pressed left the position still was (0, 2) meaning the left boundary blocked the movement | |
| FZ-TC-013 | PASS | Player position is at (0, 2) with energy shown `8/10` when pressed left the energy is not changed and remain shown `8/10`. | Blocked movement did not consume energy. |
| FZ-TC-014 | PASS | Left boundary blocks left movement, Right boundary blocks right movement, Upper boundary blocks upward movement, lower boundary blocks downward movement. | |
| FZ-TC-015 | PASS | Energy decreased to `0 / 10`, position is at (4, 4) after 10 successfull movements. | |
| FZ-TC-016 | PASS | Energy decreased to `0 / 10`, position is at (4, 4), player is not able to move due no energy as displayed energy `0 / 10`. | Succesfully drained energy and player is unable to move because of no energy. |
| FZ-TC-017 | PASS | Energy decreased to `0 / 10`, position is at (8, 6), the energy is not decreased to negative number after successfully pressing left button 10 timnes. | |
| FZ-TC-018 | PASS | Player location (2, 2) at the start, HP is located on the right and shows `HP 100/100`, energy is located on the right and shows `ENERGY: 10/10` after successfull movement to right with right button, energy changed to `ENERGY: 9 / 10`, position changed to `POSITION: (3, 2)` | |
| FZ-TC-019 | PASS | When closing FALLZONE the program shuts down correctly. | No errors when program shuts down. |

## Test Execution Summary

- Total Tests: 19
- Passed: 19
- Failed: 0
- Blocked: 0
- Not Run: 0

## Overall Result

FALLZONE v0.0001 passed all planned manual functional tests.