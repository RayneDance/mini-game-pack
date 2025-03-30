class EventBus:
    def __init__(self):
        self._listeners = []

    def subscribe(self, listener: callable):
        self._listeners.append(listener)

    def unsubscribe(self, listener: callable):
        self._listeners.remove(listener)

    def emit(self, **kwargs):
        for listener in self._listeners:
            listener(**kwargs)

class Events:
    def __init__(self):
        self.collusion = EventBus()
        self.pre_tick = EventBus()
        self.tick = EventBus()
        self.late_tick = EventBus()
        self.quit = EventBus()
        self.key_down = EventBus()
        self.key_up = EventBus()
        self.key_pressed = EventBus()
        self.mouse_button_down = EventBus()
        self.steam_achievements = EventBus()

class PygameEvents:
    def __init__(self, events: Events, pygame, engine):
        self.events = events
        self.events.pre_tick.subscribe(self.process_events)
        self.pygame = pygame
        self.engine = engine

    def process_events(self):
        self.engine.key_state = self.pygame.key.get_pressed()
        for event in self.pygame.event.get():
            if event.type == self.pygame.QUIT:
                self.events.quit.emit()

            elif event.type == self.pygame.KEYDOWN:
                self.events.key_down.emit(key=event.key)

            elif event.type == self.pygame.KEYUP:
                self.events.key_up.emit(key=event.key)

            elif event.type == self.pygame.MOUSEBUTTONDOWN:
                self.events.mouse_button_down.emit(pos=event.pos, button=event.button)