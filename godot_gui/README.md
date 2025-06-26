# RAM Overclocking Simulator - Godot GUI

This is a Godot 4.2+ GUI implementation of the RAM Overclocking Simulator. The game logic has been ported from Python to GDScript.

## Project Structure

```
godot_gui/
├── project.godot          # Main project file
├── scenes/               # Game scenes
│   ├── MainMenu.tscn     # Main menu
│   ├── NewGame.tscn      # New game setup (RAM/controller selection)
│   └── OverclockingLab.tscn  # Main overclocking interface
├── scripts/              # GDScript files
│   ├── MainMenu.gd       # Main menu controller
│   ├── NewGame.gd        # New game controller
│   ├── OverclockingLab.gd # Overclocking lab controller
│   └── GameData.gd       # Game data structures and logic
└── assets/              # Game assets
    └── themes/          # UI themes
        └── main_theme.tres  # Main UI theme

```

## Features Implemented

- **Main Menu**: Start new game, load game, access knowledge base
- **RAM Selection**: Choose from 20 different RAM kits (10 DDR4, 10 DDR5)
- **Memory Controller Selection**: Choose from 4 different controllers
- **Overclocking Lab**: 
  - Frequency adjustment with slider
  - Primary timings adjustment (CL, tRCD, tRP, tRAS)
  - Voltage adjustment (DRAM, VCCIO, VCCSA)
  - Apply XMP profiles
  - Reset to JEDEC defaults
  - Basic stress testing simulation

## Game Data Structure

The game uses GDScript classes to represent:
- `MemoryModule`: RAM kit specifications and current state
- `MemoryController`: IMC properties and settings
- IC types and their characteristics
- Real-world RAM kits with accurate specifications

## Running the Project

1. Open Godot 4.2 or later
2. Import the project by selecting the `project.godot` file
3. Press F5 or click the play button to run

## Future Enhancements

- Knowledge base scene implementation
- Save/load game functionality
- Advanced stress testing with visual feedback
- Temperature monitoring graphs
- Achievement system
- Sound effects and animations
- More detailed overclocking options (secondary timings, etc.)