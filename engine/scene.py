# Create a new file: engine/scene.py

import abc

from engine.gameobj import Entity


class Scene(abc.ABC):
    """Abstract Base Class for all game scenes."""
    def __init__(self, engine, scene_manager):
        self.engine = engine
        self.scene_manager = scene_manager
        self._entities = [] # Keep track of entities created by this scene
        self._listeners = [] # Keep track of listeners subscribed by this scene

    @abc.abstractmethod
    def load(self):
        pass

    @abc.abstractmethod
    def unload(self):
        print(f"Unloading Scene: {self.__class__.__name__}")
        self.unsubscribe_all()
        self.destroy_all_entities()

    def update(self, dt):
        pass

    # --- Helper methods for scene management ---

    def add_entity(self, entity):
        """
        Registers an entity to this scene for later cleanup.
        Does NOT add it to the engine list (create_entity does that).
        """
        if entity not in self._entities:
            self._entities.append(entity)
        return entity # Return for chaining or direct use

    def create_entity(self, entity_class, *args, **kwargs):
        """
        Instantiates an entity of the specified class, adds it to the
        engine's global list, and registers it to this scene for cleanup.

        Args:
            entity_class: The specific class to instantiate (e.g., TextEntity, Player).
            *args: Positional arguments for the entity_class constructor.
            **kwargs: Keyword arguments for the entity_class constructor.

        Returns:
            The newly created entity instance.
        """
        # Instantiate the specific entity class
        # This assumes the entity_class constructor takes the necessary arguments
        entity_instance = entity_class(*args, **kwargs)

        # --- Add the created instance to the engine's global list ---
        # Check if it's actually an Entity (optional sanity check)
        if not isinstance(entity_instance, Entity):
             raise TypeError(f"Class {entity_class.__name__} did not create an instance of Entity")

        if entity_instance not in self.engine.entities:
            self.engine.entities.append(entity_instance)
        else:
            # This might happen if an entity's __init__ somehow adds itself, which it shouldn't
            print(f"Warning: Entity {entity_instance} was already in the engine list during Scene.create_entity.")

        # --- Track the entity within the scene for cleanup ---
        # Call the modified add_entity which just adds to self._entities
        self.add_entity(entity_instance)

        return entity_instance

    def destroy_entity(self, entity):
        """Removes an entity from the engine and the scene's tracking list."""
        # Remove from scene tracking first
        if entity in self._entities:
            self._entities.remove(entity)

        # Now remove from engine's list
        if entity in self.engine.entities:
            # Deactivate first (important if it unsubscribes from events/systems)
            # Ensure set_active exists and works correctly
            if hasattr(entity, 'set_active'):
                 entity.set_active(False)
            else:
                 # Fallback if set_active isn't implemented on a base GameObject perhaps
                 entity.active = False

            try:
                self.engine.entities.remove(entity)
            except ValueError:
                # Should not happen if it was checked before, but good practice
                print(f"Warning: Entity {entity} not found in engine list during destroy (internal error?).")
        else:
            # This might happen if destroy_entity is called twice on the same entity
            print(f"Warning: Entity {entity} was already removed from engine list or never added.")

    def destroy_all_entities(self):
        """Destroys all entities registered by this scene."""
        # Iterate over a copy because destroy_entity modifies the list
        for entity in self._entities[:]:
            self.destroy_entity(entity)
        self._entities.clear() # Ensure list is empty

    def subscribe(self, event_bus, listener):
        """Subscribes a listener and tracks it for automatic unsubscribing."""
        event_bus.subscribe(listener)
        self._listeners.append((event_bus, listener))

    def unsubscribe(self, event_bus, listener):
        """Unsubscribes a listener and removes it from tracking."""
        event_bus.unsubscribe(listener)
        if (event_bus, listener) in self._listeners:
            self._listeners.remove((event_bus, listener))

    def unsubscribe_all(self):
        """Unsubscribes all listeners tracked by this scene."""
        for event_bus, listener in self._listeners:
            # Use try-except in case listener was already somehow removed
            try:
                event_bus.unsubscribe(listener)
            except Exception as e:
                print(f"Warning: Error unsubscribing listener {listener}: {e}")
        self._listeners.clear()

    def draw_overlay(self, surface):
        """
        Optional method for scenes to draw directly onto the screen surface
        after all entities have been rendered by the RenderSystem.
        Called by the Engine loop.

        Args:
            surface (pygame.Surface): The main screen surface to draw on.
        """
        pass