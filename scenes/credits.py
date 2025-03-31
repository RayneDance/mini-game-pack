import pygame
import webbrowser
# Engine/Scene imports
# Need Transform and Render for centering logic adjustment
from engine.components.transform import Transform
from engine.components.render import Render
from engine.components.drawables import DrawDepth # Assuming DrawDepth is in drawables.py
from engine.scene import Scene
from engine.ui.text_entity import TextEntity

# Constants for Credits Scene
TITLE_FONT_SIZE = 48
CATEGORY_FONT_SIZE = 32
ITEM_FONT_SIZE = 26
LINK_FONT_SIZE = 22
TEXT_COLOR = (230, 230, 230)
CATEGORY_COLOR = (180, 220, 255) # Light blue for category titles
LINK_COLOR = (100, 150, 255) # Brighter blue for links
LINE_SPACING_SMALL = 25
LINE_SPACING_LARGE = 40
TOP_MARGIN = 50
BACKGROUND_COLOR = (25, 25, 45) # Darker purple/blue

class CreditsScene(Scene): # Changed class name to CreditsScene for consistency
    def load(self):
        print("CreditsScene Loading...")
        self.engine.render_system.set_background_color(BACKGROUND_COLOR)

        screen_width = self.engine.screen.width
        self.text_entities = [] # Store all created text entities for potential management
        current_y = TOP_MARGIN

        # --- Helper function for creating and centering text lines ---
        def add_centered_line(text, size, color, y_pos, url=None):
            # Step 1: Create entity, initial x at screen center
            entity = self.create_entity(TextEntity,
                text=text,
                font_name=None,
                font_size=size,
                color=color,
                engine=self.engine,
                x=screen_width // 2, # Initial X pos
                y=y_pos,
                depth=DrawDepth.UI
            )
            # Step 2: Adjust x based on rendered width
            try: # Use try-except for robustness
                 if Render in entity.components and entity.components[Render].texture:
                     entity_width = entity.components[Render].texture.get_width()
                     entity.components[Transform].x -= entity_width // 2 # Shift left
                 else:
                      print(f"Warning: Could not get width for credit line: '{text}'")
            except Exception as e:
                 print(f"Error centering text '{text}': {e}")
            if url:
                entity.url = url
            self.text_entities.append(entity)
            return entity # Return entity if needed

        # --- Add Credit Lines ---

        # Title
        add_centered_line("Credits", TITLE_FONT_SIZE, TEXT_COLOR, current_y)
        current_y += LINE_SPACING_LARGE * 1.5 # Extra space after title

        # Libraries Section
        add_centered_line("Libraries", CATEGORY_FONT_SIZE, CATEGORY_COLOR, current_y)
        current_y += LINE_SPACING_SMALL

        add_centered_line("Pygame", ITEM_FONT_SIZE, TEXT_COLOR, current_y)
        current_y += LINE_SPACING_SMALL * 0.8
        add_centered_line("https://www.pygame.org/", LINK_FONT_SIZE, LINK_COLOR, current_y, url="https://www.pygame.org/")
        current_y += LINE_SPACING_LARGE

        add_centered_line("SteamworksPy", ITEM_FONT_SIZE, TEXT_COLOR, current_y)
        current_y += LINE_SPACING_SMALL * 0.8
        add_centered_line("https://github.com/philippj/SteamworksPy", LINK_FONT_SIZE, LINK_COLOR, current_y, url="https://github.com/philippj/SteamworksPy") # Corrected link (assuming Gramps fork is used)
        # Note: If using philippj's original, adjust link. Ensure you credit the correct one.
        current_y += LINE_SPACING_LARGE

        # Assets Section
        add_centered_line("Assets", CATEGORY_FONT_SIZE, CATEGORY_COLOR, current_y)
        current_y += LINE_SPACING_SMALL

        add_centered_line("52 Card Decks - More Than Just A Game", ITEM_FONT_SIZE, TEXT_COLOR, current_y)
        current_y += LINE_SPACING_SMALL * 0.8
        add_centered_line("https://www.fab.com/...", LINK_FONT_SIZE, LINK_COLOR, current_y, url="https://www.fab.com/listings/57e8bc76-6f19-4b5e-bf09-e912eba4c88f") # Truncated link for display
        # Note: The fab.com link might be transient or lead to a specific product listing.
        # Consider finding a more permanent link to the asset creator/source if possible.
        current_y += LINE_SPACING_LARGE

        add_centered_line("Music", CATEGORY_FONT_SIZE, CATEGORY_COLOR, current_y)
        current_y += LINE_SPACING_SMALL
        add_centered_line("Alonzo Suarez", ITEM_FONT_SIZE, TEXT_COLOR, current_y)
        current_y += LINE_SPACING_SMALL
        add_centered_line("YouTube", ITEM_FONT_SIZE, LINK_COLOR, current_y, url="https://www.youtube.com/@StonePanda")
        current_y += LINE_SPACING_LARGE
        add_centered_line("Austin Trevino", ITEM_FONT_SIZE, TEXT_COLOR, current_y)
        current_y += LINE_SPACING_SMALL
        add_centered_line("Linktr.ee", ITEM_FONT_SIZE, LINK_COLOR, current_y, url="https://linktr.ee/cursedatx")
        current_y += LINE_SPACING_LARGE

        # Add more sections/items as needed (e.g., Developer, Engine, Fonts, Music)

        # Return Instructions
        current_y += LINE_SPACING_SMALL # Space before instructions
        add_centered_line("Press ESC to return to Main Menu", ITEM_FONT_SIZE, TEXT_COLOR, current_y)


        # --- Subscribe to Input ---
        # Use self.subscribe for automatic cleanup
        self.subscribe(self.engine.events.key_down, self.handle_input)
        self.subscribe(self.engine.events.mouse_button_down, self.handle_mouse_click)


    def unload(self):
        # self.unsubscribe(self.engine.events.key_down, self.handle_input) # Handled by super().unload()
        super().unload()
        print("CreditsScene Unloaded.")

    # update method is optional if no per-frame logic is needed in the scene itself
    # def update(self, dt):
    #     pass

    def handle_input(self, key):
        if key == pygame.K_ESCAPE:
            print("ESC pressed in Credits, returning to menu.")
            self.scene_manager.set_active_scene("main_menu")

    def handle_mouse_click(self, pos, button):
        """Checks if a mouse click hit any text entity with a URL."""
        if button != 1:  # Only handle left clicks
            return

        for entity in self.text_entities:
            # Check if this entity has a URL attached
            url_to_open = getattr(entity, 'url', None)  # Safely get 'url' attribute

            if url_to_open:
                # Get components needed for collision check
                transform = entity.components.get(Transform)
                render = entity.components.get(Render)

                # Check if components and texture exist
                if not (transform and render and render.texture):
                    continue  # Skip if entity isn't ready

                # Get the rectangle bounds
                entity_rect = render.texture.get_rect(topleft=(transform.x, transform.y))

                # Check if the click position is inside the rectangle
                if entity_rect.collidepoint(pos):
                    print(f"Link clicked: {url_to_open}")
                    try:
                        # Open the URL in the default web browser
                        webbrowser.open(url_to_open)
                        # Optional: Change link color briefly on click? (More complex)
                    except Exception as e:
                        print(f"Error opening URL '{url_to_open}': {e}")
                    # Stop checking other entities once a link is clicked
                    break