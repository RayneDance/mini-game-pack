class SceneManager:
    def __init__(self, engine):
        self.engine = engine
        self._scenes = {}
        self.active_scene = None
        self.active_scene_name = None
        # Subscribe the manager's update to the engine tick
        self.engine.events.tick.subscribe(self._update_active_scene)

    def register_scene(self, name: str, scene: 'Scene'):
        """Stores a scene instance, ready to be activated."""
        if name in self._scenes:
            print(f"Warning: Scene name '{name}' already registered. Overwriting.")
        self._scenes[name] = scene
        print(f"Scene '{name}' registered ({scene.__class__.__name__})")

    def set_active_scene(self, name: str):
        """Switches the active scene."""
        if name not in self._scenes:
            print(f"Error: Cannot set active scene. Scene '{name}' not registered.")
            return
        if self.active_scene_name == name:
            print(f"Warning: Scene '{name}' is already active.")
            return

        print(f"Changing scene from '{self.active_scene_name}' to '{name}'...")

        # Unload the current scene if there is one
        if self.active_scene:
            self.active_scene.unload() # Calls entity destruction, unsubscribes listeners

        # Set and load the new scene
        self.active_scene_name = name
        self.active_scene = self._scenes[name]
        self.active_scene.load() # Creates new entities, subscribes listeners
        print(f"Scene '{name}' loaded and active.")


    def _update_active_scene(self, dt):
        """Internal method called by engine tick to update the active scene."""
        if self.active_scene:
            self.active_scene.update(dt) # Call the scene's own update method