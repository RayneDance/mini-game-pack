import pygame

from engine import Render, Transform
# Relative imports to access engine components (adjust if your structure differs)
from engine.scene import Scene
from engine.ui.text_entity import TextEntity

# Constants specific to the Main Menu
# NOTE: SCREEN_WIDTH/HEIGHT are now accessed via self.engine.screen
MENU_FONT_NAME = None # Use Pygame default font
MENU_FONT_SIZE = 48
MENU_ITEM_FONT_SIZE = 36
TEXT_COLOR = (230, 230, 230) # Light grey/white
HIGHLIGHT_COLOR = (255, 255, 0) # Yellow


class MainMenuScene(Scene):
    def load(self):
        print("MainMenuScene Loading...")
        screen_width = self.engine.screen.width
        screen_height = self.engine.screen.height

        # --- Create Title (no changes needed) ---
        self.title = self.create_entity(TextEntity,
            text="Main Menu", font_name=MENU_FONT_NAME, font_size=MENU_FONT_SIZE,
            color=TEXT_COLOR, engine=self.engine, x=screen_width // 2, y=100
        )
        if Render in self.title.components and self.title.components[Render].texture:
            title_width = self.title.components[Render].texture.get_width()
            self.title.components[Transform].x -= title_width // 2

        # --- Create Menu Items (no changes needed) ---
        self.menu_options = ["Snake", "Blackjack", "Roadrunner", "Credits", "Quit"]
        self.menu_entities = []
        self.selected_index = 0
        start_y = 200
        y_spacing = 60
        for i, option in enumerate(self.menu_options):
            entity = self.create_entity(TextEntity,
                text=option, font_name=MENU_FONT_NAME, font_size=MENU_ITEM_FONT_SIZE,
                color=TEXT_COLOR, engine=self.engine,
                x=screen_width // 2, y = start_y + i * y_spacing
            )
            if Render in entity.components and entity.components[Render].texture:
                text_width = entity.components[Render].texture.get_width()
                entity.components[Transform].x -= text_width // 2
            self.menu_entities.append(entity)

        self._update_highlight()

        # --- Subscribe to Inputs ---
        self.subscribe(self.engine.events.key_down, self.handle_input)
        # Subscribe to the new mouse click event
        self.subscribe(self.engine.events.mouse_button_down, self.handle_mouse_click)


    def unload(self):
        super().unload()
        print("MainMenuScene Unloaded.")

    # --- Input Handlers ---

    def handle_input(self, key):
        # Keyboard navigation remains the same
        if key == pygame.K_UP or key == pygame.K_w or key == pygame.K_k:
            self.selected_index = (self.selected_index - 1) % len(self.menu_options)
            self._update_highlight()
        elif key == pygame.K_DOWN or key == pygame.K_s or key == pygame.K_j:
            self.selected_index = (self.selected_index + 1) % len(self.menu_options)
            self._update_highlight()
        elif key == pygame.K_RETURN or key == pygame.K_SPACE:
            self.select_option()

    def handle_mouse_click(self, pos, button):
        """Checks if a mouse click hit any menu item."""
        if button != 1: # Only respond to left clicks
            return

        print(f"Mouse click at {pos}") # Debug print

        for i, entity in enumerate(self.menu_entities):
            # Get components needed for position and size
            transform = entity.components.get(Transform)
            render = entity.components.get(Render)

            # Check if components and texture exist
            if not (transform and render and render.texture):
                continue # Skip if entity isn't fully formed or visible

            # Get the rectangle bounds of the text entity
            entity_rect = render.texture.get_rect(topleft=(transform.x, transform.y))

            # Check if the click position is inside the rectangle
            if entity_rect.collidepoint(pos):
                print(f"Clicked on: {self.menu_options[i]}")
                # If clicked, select this item and trigger the action
                self.selected_index = i
                self._update_highlight() # Update visual highlight immediately
                self.select_option()     # Trigger the same action as Enter/Space
                break # Stop checking other items once one is clicked

    # --- Helper Methods ---

    def _update_highlight(self):
        # Add a check for menu_entities existence for safety
        if not hasattr(self, 'menu_entities'):
             return
        for i, entity in enumerate(self.menu_entities):
            # Extra check for entity validity before changing color
            if entity and hasattr(entity, 'color'):
                 entity.color = HIGHLIGHT_COLOR if i == self.selected_index else TEXT_COLOR

    def select_option(self):
        # Add a check for menu_options existence
        if not hasattr(self, 'menu_options') or not self.menu_options:
            return
        # Ensure selected_index is valid (though modulo usually handles this)
        if not (0 <= self.selected_index < len(self.menu_options)):
            print(f"Warning: Invalid selected_index {self.selected_index}")
            return

        selected_option = self.menu_options[self.selected_index]
        print(f"Selected: {selected_option}")
        # Navigation logic remains the same

        match selected_option:
            case "Snake":
                self.scene_manager.set_active_scene("snake")
            case "Blackjack":
                self.scene_manager.set_active_scene("blackjack")
            case "Roadrunner":
                self.scene_manager.set_active_scene("roadrunner")
            case "Credits":
                self.scene_manager.set_active_scene("credits")
            case "Quit":
                self.engine.exit()