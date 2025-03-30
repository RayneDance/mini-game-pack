from engine.components.drawables import DrawDepth
from engine.components.transform import Transform
from engine.components.render import Render
import pygame

class GameObject:
    def __init__(self, events):
        self.components = {}
        self.events = events


class Entity(GameObject):
    def __init__(self, transform, render, events, collision_system=None):
        super().__init__(events)
        self.components[Transform] = transform
        self.components[Render] = render
        self.active = True
        self._collider = None
        self.collision_system = collision_system
        self.set_active(True)

    @property
    def collider(self):
        return self._collider

    @collider.setter
    def collider(self, new_collider):
        # Unregister old collider if it exists and system is known
        if self._collider and self.collision_system:
             self.collision_system.unregister_collider(self._collider)

        self._collider = new_collider
        # Register new collider if it exists and system is known
        if self._collider and self.collision_system and self.active:
             self.collision_system.register_collider(self._collider)

    # Method to easily set texture for convenience
    def set_texture(self, texture: pygame.Surface):
         if Render in self.components:
              self.components[Render].set_texture(texture)
         else:
              # Handle error or log warning: Cannot set texture, Render component missing
              print(f"Warning: Entity {self} does not have a Render component.")

    # Method to easily set visibility
    def set_visible(self, visible: bool):
         if Render in self.components:
              self.components[Render].set_visible(visible)
         else:
              print(f"Warning: Entity {self} does not have a Render component.")

    # Method to set draw depth
    def set_draw_depth(self, depth: DrawDepth):
        if Render in self.components:
            self.components[Render].set_draw_depth(depth)
        else:
            print(f"Warning: Entity {self} does not have a Render component.")

    def set_active(self, active: bool):
        self.active = active

        if self.collider and self.collision_system:
            if self.active:
                self.collision_system.register_collider(self.collider)
            else:
                self.collision_system.unregister_collider(self.collider)