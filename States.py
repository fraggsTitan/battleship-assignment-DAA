from enum import Enum

class CellState(Enum):
    UNKNOWN = 0
    HIT = 1
    MISS = 2

class AIMode(Enum):
    HUNTING = 1
    TARGETING = 2