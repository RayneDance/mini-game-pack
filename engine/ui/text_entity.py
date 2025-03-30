# Create a new file: engine/ui/text_entity.py (or similar path)

import pygame
from engine.gameobj import Entity
from engine.components.transform import Transform
from engine.components.render import Render
from engine.components.drawables import DrawDepth

class TextEntity(Entity):
    """An Entity specialized for rendering text."""

    def __init__(self, text: str, font_name: str, font_size: int, color: tuple,
                 engine, collision_system=None, # Pass engine to access RM
                 x=0, y=0, depth=DrawDepth.UI, antialias=True):

        self._font_name = font_name
        self._font_size = font_size
        self._color = color
        self._text = text
        self._antialias = antialias
        self.engine = engine # Needed for resource manager

        # Initialize components
        transform = Transform(x, y)
        render = Render()
        render.set_draw_depth(depth)

        # Call parent Entity init AFTER components are ready
        super().__init__(transform, render, engine.events, collision_system)

        # Render initial text surface
        self._update_texture()


    def _update_texture(self):
        """Renders the text to a surface and sets it as the Render texture."""
        font = self.engine.resource_manager.get_font(self._font_name, self._font_size)
        if not font:
            print(f"Error: Font '{self._font_name}' size {self._font_size} not loaded for TextEntity.")
            # Use fallback image from RM if font fails? Or create dynamic fallback text?
            fallback_surface = pygame.Surface((50, 20))
            fallback_surface.fill((255,0,0)) # Red indicates error
            self.set_texture(fallback_surface)
            return

        try:
            text_surface = font.render(self._text, self._antialias, self._color)
            self.set_texture(text_surface)
            # Optional: update collider size if needed based on text rect?
            # if self.collider: self.set_collider_size(text_surface.get_size())
        except Exception as e:
            print(f"Error rendering text '{self._text}': {e}")
            # Set fallback texture on render error
            fallback_surface = pygame.Surface((50, 20))
            fallback_surface.fill((255,0,0))
            self.set_texture(fallback_surface)


    # --- Properties to change text dynamically ---

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        if self._text != value:
            self._text = value
            self._update_texture() # Re-render the text surface

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        if self._color != value:
            self._color = value
            self._update_texture()