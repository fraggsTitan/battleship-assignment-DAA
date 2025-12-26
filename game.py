# game.py
from board import Board, SHIP, HIT, MISS, EMPTY, SHIP_SIZES
from ai import BattleshipAI

 
class BattleshipGame:
    def __init__(self):
        self.player_board = Board()
        self.ai_board = Board()
        self.ai = BattleshipAI()

        # tracking boards (what each side sees)
        self.player_view = Board()
        self.ai_view = Board()

        # place ships
        # player ships will be placed via UI; only AI auto‑place here
        self.ai_board.random_place_ships(SHIP_SIZES)
        self.current_turn = "PLAYER"

    # called by UI during placement
    def player_can_place(self, r, c, length, orient):
        return self.player_board.can_place_ship(r, c, length, orient)

    def player_place(self, r, c, length, orient):
        self.player_board.place_ship(r, c, length, orient)

    def all_player_ships_placed(self):
        # naive check: count S cells
        total = sum(row.count(SHIP) for row in self.player_board.grid)
        return total == sum(SHIP_SIZES)

    # gameplay methods
    def player_shoot(self, r, c):
        cell = self.ai_board.grid[r][c]
        if cell in (HIT, MISS):
            return "REPEAT"
        result = self.ai_board.receive_shot(r, c)
        # mirror to what player sees
        if result == "HIT":
            self.player_view.grid[r][c] = HIT
        elif result == "MISS":
            self.player_view.grid[r][c] = MISS
        return result

    def ai_shoot(self):
        r, c = self.ai.get_shot(self.ai_view)
        result = self.player_board.receive_shot(r, c)

        self.ai.update_after_shot(r, c, result, self.ai_view)

        if result == "HIT":
            self.ai_view.grid[r][c] = HIT
        elif result == "MISS":
            self.ai_view.grid[r][c] = MISS

        return r, c, result


    def player_won(self):
        return self.ai_board.all_ships_sunk()

    def ai_won(self):
        return self.player_board.all_ships_sunk()
