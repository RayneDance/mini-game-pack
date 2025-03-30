from enum import Enum

class DrawDepth(Enum):
    BACKGROUND = 0
    TERRAIN = 1
    OBJECT = 2
    UI = 3
    DEFAULT = 4