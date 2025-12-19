# Controller.py
from Graph import Board
from Player import Player
from CPU import CPU
from States import GameState


class Controller:
    def __init__(self):
        self.size = 10
        self.player_board = Board(self.size)
        self.cpu_board = Board(self.size)

        self.player = Player("You", self.player_board)
        self.cpu = CPU(self.size)

        self._place_fleet(self.player_board)
        self._place_fleet(self.cpu_board)

        self.state = GameState.PLAYER_TURN

    def _place_fleet(self, board):
        for L in [5, 4, 3, 3, 2]:
            board.place_ship_random(L)

    def player_shot(self, r, c):
        result = self.cpu_board.receive_shot(r, c)
        if self.cpu_board.all_sunk():
            self.state = GameState.GAME_OVER
        else:
            # only give CPU a turn if shot wasn't invalid/repeat/out
            if result not in ("REPEAT", "OUT"):
                self.state = GameState.CPU_TURN
        return result

    def cpu_turn(self):
        r, c = self.cpu.choose_shot(self.player_board)
        result = self.player_board.receive_shot(r, c)
        self.cpu.notify_result(r, c, result, self.player_board)

        if self.player_board.all_sunk():
            self.state = GameState.GAME_OVER
        else:
            if result not in ("REPEAT", "OUT"):
                self.state = GameState.PLAYER_TURN

        return r, c, result

    def is_over(self):
        return self.state == GameState.GAME_OVER
