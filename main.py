import pygame

from engine import Render, Transform
from engine.engine import Engine
from engine.scene import Scene
from engine.ui.text_entity import TextEntity
from scenes.blackjack_scene import BlackjackScene
from scenes.main_menu_scene import MainMenuScene
from scenes.snake_scene import SnakeScene

# --- Global Constants ---
# Constants needed by main setup or potentially shared (like screen size)
# --- Game Constants ---
# Define Snake Grid parameters here
SNAKE_GRID_WIDTH = 26
SNAKE_GRID_HEIGHT = 20
SNAKE_TILE_SIZE = 30
# Calculate screen size based on Snake grid
# Note: Other games might need different sizes, requiring window resizing later
SCREEN_WIDTH = SNAKE_GRID_WIDTH * SNAKE_TILE_SIZE
SCREEN_HEIGHT = SNAKE_GRID_HEIGHT * SNAKE_TILE_SIZE

class PlaceholderScene(Scene):
    """A simple placeholder for minigames."""
    def __init__(self, engine, scene_manager, game_name):
        super().__init__(engine, scene_manager)
        self.game_name = game_name
        # Constants needed by placeholder
        self.font_name = None
        self.font_size = 48
        self.item_font_size = 36
        self.text_color = (230, 230, 230)

    def load(self):
        print(f"{self.game_name} Scene Loading...")
        screen_width = self.engine.screen.width
        screen_height = self.engine.screen.height

        # Display game name
        self.title = self.create_entity(TextEntity,
            text=f"{self.game_name} - Placeholder",
            font_name=self.font_name,
            font_size=self.font_size,
            color=self.text_color,
            engine=self.engine,
            x=screen_width // 2, y=screen_height // 2 - 50
        )
        # Check if texture exists before getting width (robustness)
        if hasattr(self.title.components.get(Render), 'texture') and \
           self.title.components[Render].texture:
             title_width = self.title.components[Render].texture.get_width()
             self.title.components[Transform].x -= title_width // 2

        # Display return instruction
        self.instructions = self.create_entity(TextEntity,
            text="Press ESC to return to Main Menu",
            font_name=self.font_name,
            font_size=self.item_font_size,
            color=self.text_color,
            engine=self.engine,
            x=screen_width // 2, y=screen_height // 2 + 50
        )
        if hasattr(self.instructions.components.get(Render), 'texture') and \
           self.instructions.components[Render].texture:
            inst_width = self.instructions.components[Render].texture.get_width()
            self.instructions.components[Transform].x -= inst_width // 2

        # Subscribe ESC key to return
        self.subscribe(self.engine.events.key_down, self.handle_input)

    def unload(self):
        super().unload()
        print(f"{self.game_name} Scene Unloaded.")

    def handle_input(self, key):
        if key == pygame.K_ESCAPE:
            print(f"ESC pressed in {self.game_name}, returning to menu.")
            self.scene_manager.set_active_scene("main_menu")

# --- Main Execution ---
if __name__ == "__main__":
    print("Initializing...")
    # Create Engine instance
    engine = Engine(pygame, fps_limit=60, assets_path="assets")
    # Set screen size properties AFTER engine init
    engine.screen.width = SCREEN_WIDTH
    engine.screen.height = SCREEN_HEIGHT
    engine.screen.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Minigame Hub")
    engine.render_system.set_background_color((20, 20, 50)) # Dark blue background

    # Get the scene manager from the engine
    scene_manager = engine.scene_manager

    # --- Create Scene Instances ---
    # Instantiate MainMenuScene using the imported class
    main_menu = MainMenuScene(engine, scene_manager)
    # Instantiate placeholders (consider moving them later too)
    snake_game = SnakeScene(engine, scene_manager, grid_width=SNAKE_GRID_WIDTH, grid_height=SNAKE_GRID_HEIGHT, tile_size=SNAKE_TILE_SIZE)
    blackjack_game = BlackjackScene(engine, scene_manager)
    roadrunner_game = PlaceholderScene(engine, scene_manager, "Roadrunner")

    # Register Scenes
    scene_manager.register_scene("main_menu", main_menu)
    scene_manager.register_scene("snake", snake_game)
    scene_manager.register_scene("blackjack", blackjack_game)
    scene_manager.register_scene("roadrunner", roadrunner_game)

    print(engine.steamworks_system.get_achievement_status(achievement_api_name="SNAKE_30"))

    # Set Initial Scene
    scene_manager.set_active_scene("main_menu")

    # Start the Engine's Main Loop
    engine.start()

    print("Application Finished.")