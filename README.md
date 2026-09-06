# DoDA - GZDoom Tactical Mod

## Overview
DoDA implements custom weapon systems, mission management, and advanced character mechanics (like leaning and deadzone aiming) to the GZDoom engine.

## Requirements
*   **Engine:** [GZDoom](https://zdoom.org/downloads) (latest version recommended)
*   **Game:** A base Doom IWAD (e.g., `doom.wad`, `doom2.wad`)

## Setup / Running
1.  Ensure you have GZDoom installed.
2.  Launch GZDoom by loading the `doda-core` directory or creating a PK3 file from it.
    *   Command line example: `gzdoom.exe -file path/to/doda-core`

## Project Structure
The project is organized into several key modules defined in `zscript.txt`:

*   `Aim`: Aiming mechanics and input handling.
*   `CharacterClasses`: Player classes (`FieldAgent`, `Analyst`, `SAC`).
*   `UI`: HUD and user interface elements.
*   `Abilities`: Character abilities like leaning.
*   `WeaponSystem`: Weapon logic, animation, and pistol implementation.
*   `MissionSystem`: Mission management, campaign state, and mission objects.

## Scripts & Development
The project is built using **ZScript** (version 2.4). The main entry point is `zscript.txt`.

### TODOs
*   Refactor `WeaponBase.zs` to move lean ability logic to `DoDA/Abilities/Lean/`.
*   Fix `HUDDeadzone` rendering issues in Deadzone Aim Mode.
*   Refactor and organize `CVARINFO`, `KEYCONF`, and `MENUDEF`.
*   Improve Deadzone Aim System camera locking functionality.

## Testing
Testing is performed in-game within GZDoom. 
*   Use `DebugTrigger.zs` for mission-related debugging.

## License
*   [TODO: Add license information]
