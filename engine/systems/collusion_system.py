from engine.components.transform import Transform
from engine.gameobj import Entity

class CollisionSystem:
    def __init__(self, engine):
        self.engine = engine
        self.events = engine.events
        self.colliders = []
        self.events.pre_tick.subscribe(self.update)

    def register_collider(self, collider):
        if collider not in self.colliders:
            self.colliders.append(collider)

    def unregister_collider(self, collider):
        if collider in self.colliders:
            self.colliders.remove(collider)

    def update(self):

        collidable_entities = [
            entity for entity in self.engine.entities
            if entity.active and hasattr(entity, 'collider') and entity.collider is not None
               and Transform in entity.components # Explicitly check for Transform
        ]

        # Basic O(n^2) pair checking
        for i in range(len(collidable_entities)):
            for j in range(i + 1, len(collidable_entities)):
                entity_a = collidable_entities[i]
                entity_b = collidable_entities[j]

                collider_a = entity_a.collider
                collider_b = entity_b.collider

                # Perform the intersection check using the colliders
                if collider_a.intersects(collider_b):
                    # Emit ONE event for this pair
                    self.events.collusion.emit(
                        entity_a=entity_a,
                        entity_b=entity_b,
                        collider_a=collider_a,
                        collider_b=collider_b
                    )