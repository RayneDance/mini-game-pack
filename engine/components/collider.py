from engine.components.transform import Transform


class Collider:
    def __init__(self, parent, events):
        self.events = events
        self.parent = parent


class BoxCollider(Collider):
    def __init__(self, parent, events, rect: tuple):
        super().__init__(parent, events)
        self.rect = rect

    @property
    def rect(self):
         return self.width, self.height

    @rect.setter
    def rect(self, value: tuple):
         self.width = value[0]
         self.height = value[1]


    def intersects(self, other) -> bool:
        if Transform not in self.parent.components or Transform not in other.parent.components:
             return False

        self_pos = (self.parent.components[Transform].x, self.parent.components[Transform].y)
        other_pos = (other.parent.components[Transform].x, other.parent.components[Transform].y)
        
        self_left = self_pos[0]
        self_top = self_pos[1]
        self_right = self_pos[0] + self.width
        self_bottom = self_pos[1] + self.height

        other_left = other_pos[0]
        other_top = other_pos[1]
        other_right = other_pos[0] + other.width 
        other_bottom = other_pos[1] + other.height
        
        return (
            self_left < other_right and
            self_right > other_left and
            self_top < other_bottom and
            self_bottom > other_top
        )
