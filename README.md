# Python Minigame Hub

A collection of simple minigames built using Python and Pygame, featuring a custom game engine foundation and managed with the `uv` package manager.

At this point, I'm not sure what code is mine, and what was vibe coded with reckless abandon. The serious spaghetti is mostly the doing of Gemini.

## Features

*   **Main Menu:** Navigate using keyboard (Arrows/WASD, Enter/Space) or Mouse Clicks to select a game.
*   **Multiple Minigames:**
    *   **Snake:** Classic snake game implementation. Control the snake to eat food and grow longer.
    *   **Blackjack:** Text-based Blackjack implementation. Try to beat the dealer!
    *   **Roadrunner:** (Placeholder)
*   **Custom Engine:** Built with a basic Entity-Component-System (ECS) inspired structure.
*   **Scene Management:** Easily switch between the main menu and different game scenes.
*   **Resource Management:** Simple system for loading and caching assets (currently fonts, potentially images/sounds later).

## Technologies Used

*   [Python 3](https://www.python.org/)
*   [Pygame](https://www.pygame.org/) - For graphics, sound, and input handling.
*   [uv](https://github.com/astral-sh/uv) - For Python package management (environment creation and dependency installation).

## Setup and Installation

Recommend using UV, but it's honestly not a tricky project. Only depends on Pygame.

## How to Run

    ```
    uv run main.py
    ```

This will launch the Pygame window, starting with the main menu.

## Project Structure
```
mini-game-pack/
├── assets/             # Game assets (images, sounds, fonts)
│   ├── fonts/
│   ├── images/
│   └── sounds/
├── engine/             # Core game engine components
│   ├── components/     # Data components (Transform, Render, Collider, etc.)
│   │   ├── __init__.py
│   │   ├── collider.py
│   │   ├── render.py
│   │   └── transform.py
│   ├── systems/        # Logic systems (RenderSystem, CollisionSystem, etc.)
│   │   ├── __init__.py
│   │   ├── collision_system.py
│   │   └── render_system.py
│   ├── ui/             # UI specific elements
│   │   └── text_entity.py
│   ├── __init__.py     # Root engine init (defines ENGINE if used globally)
│   ├── drawables.py    # DrawDepth Enum, etc.
│   ├── engine.py       # Main engine class and loop
│   ├── events.py       # Event bus and Pygame event handling
│   ├── gameobj.py      # GameObject and Entity definitions
│   ├── resource_manager.py # Asset loading/caching
│   ├── scene.py        # Base Scene class
│   ├── scene_manager.py  # Handles scene transitions
│   └── screen.py       # Pygame screen setup
├── scenes/             # Individual game scenes/states
│   ├── __init__.py
│   ├── blackjack_scene.py
│   ├── main_menu_scene.py
│   └── snake_scene.py
├── main.py             # Main application entry point, scene setup
├── requirements.txt    # Project dependencies for uv/pip
└── README.md           # Project description and setup instructions
```

## TODO / Future Improvements

*   Implement the "Roadrunner" game.
*   Add visual card graphics to Blackjack.
*   Incorporate sound effects and background music.
*   Implement high scores for games like Snake.
*   Improve UI elements (proper buttons, visual feedback).
*   Refactor engine components for more robustness.
*   Steam?

## License

[Choose and insert your license here - e.g., MIT License]

*Consider adding a `LICENSE` file to your repository.*
You can choose a license at [https://choosealicense.com/](https://choosealicense.com/). The MIT license is a popular and permissive choice for open-source projects.