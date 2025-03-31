from engine.events import Events, PygameEvents
from engine.gameobj import GameObject, Entity
from engine.screen import Screen
from engine.components.transform import Transform
from engine.components.render import Render
from engine.systems.collusion_system import CollisionSystem
from engine.systems.render_system import RenderSystem
from engine.systems.music_system import MusicSystem
from engine.resourcemanager import ResourceManager
from engine.scene_manager import SceneManager
from engine.steamworks_sys import SteamworksSystem

class Engine:
    def __init__(self, pygame, auto_start=False, fps_limit=60, assets_path="assets"):
        pygame.init()
        self.pygame = pygame
        self.screen = Screen(pygame)
        self.fps_limit = fps_limit
        self.clock = self.pygame.time.Clock()
        self.clock.tick(fps_limit)
        self.last_tick = 0

        self.resource_manager = ResourceManager(base_path=assets_path)

        self.events = Events()
        self.events.quit.subscribe(self.exit)
        self.pygame_events = PygameEvents(self.events, pygame, engine=self)

        self.objs = []
        self.entities = []
        self.collision_system = CollisionSystem(self)
        self.render_system = RenderSystem(self)
        self.steamworks_system = SteamworksSystem(self)
        self.music_system = MusicSystem(self)
        self.systems = [self.collision_system, self.render_system, self.steamworks_system, self.music_system]

        self.scene_manager = SceneManager(self)

        if auto_start:
            self.start()
        self.running = False

    def start(self):
        """Starts the main engine loop AFTER the initial scene is set."""
        if not self.scene_manager.active_scene:
            print("ERROR: Cannot start engine. No active scene set via scene_manager.set_active_scene()")
            return

        print("Engine starting...")
        self.running = True
        while self.running:
            milliseconds = self.pygame.time.get_ticks()
            delta_time = milliseconds - self.last_tick
            self.last_tick = milliseconds
            self.events.pre_tick.emit()
            self.events.tick.emit(dt=delta_time)
            self.events.late_tick.emit()

            if self.scene_manager.active_scene:
                self.scene_manager.active_scene.draw_overlay(self.screen.screen)

            self.screen.draw()
        self.pygame.quit()

    def new_game_object(self) -> GameObject:
        obj = GameObject(self.events)
        self.objs.append(obj)
        return obj

    def new_entity(self, transform: Transform = None, render: Render = None) -> Entity:
        # Create defaults if None
        if transform is None:
            transform = Transform()
        if render is None:
            render = Render()

        entity = Entity(transform, render, self.events, self.collision_system)
        self.entities.append(entity)
        return entity

    def exit(self):
        self.running = False