# States.py
from enum import Enum


class GameState(Enum):
    PLAYER_TURN = 0
    CPU_TURN = 1
    GAME_OVER = 2
