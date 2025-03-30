# Create a new file: engine/systems/render_system.py

import pygame
from engine.components.transform import Transform
from engine.components.render import Render
from engine.components.drawables import DrawDepth # Import DrawDepth

class RenderSystem:
    def __init__(self, engine):
        """
        Initializes the Render System.

        Args:
            engine: The main engine instance, providing access to entities, screen, and events.
        """
        self.engine = engine
        self.screen_surface = engine.screen.screen # Get the Pygame surface
        # Subscribe the update method to the late_tick event
        self.engine.events.late_tick.subscribe(self.update)
        self.background_color = (0, 0, 0) # Default background: black

    def set_background_color(self, color: tuple):
        """Sets the background color used to clear the screen."""
        self.background_color = color

    def update(self):
        """
        Called once per frame (during late_tick) to draw all visible entities.
        """
        # 1. Clear the screen
        self.screen_surface.fill(self.background_color)

        # 2. Get all active entities with Transform and Render components
        drawable_entities = []
        for entity in self.engine.entities:
            if (entity.active and
                    Transform in entity.components and
                    Render in entity.components):
                render_comp = entity.components[Render]
                # Check visibility and if a texture exists
                if render_comp.visible and render_comp.texture is not None:
                    drawable_entities.append(entity)

        # 3. Sort entities by DrawDepth (lower values drawn first)
        #    We access the component and then the draw_depth Enum value
        drawable_entities.sort(key=lambda e: e.components[Render].draw_depth.value)

        # 4. Draw each entity's texture at its transform position
        for entity in drawable_entities:
            transform_comp = entity.components[Transform]
            render_comp = entity.components[Render]

            # Use integer positions for blitting
            position = (int(transform_comp.x), int(transform_comp.y))

            # Blit the texture onto the screen surface
            self.screen_surface.blit(render_comp.texture, position)

        # 5. Update the display (Handled by the engine loop after late_tick)
        #    Do NOT call pygame.display.flip() here.