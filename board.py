# board.py
import random
import string

BOARD_SIZE = 10
SHIP_SIZES = [5, 4, 3, 3, 2]

EMPTY = '.'
SHIP = 'S'
HIT = 'X'
MISS = 'O'


class Board:
    def __init__(self):
        self.size = BOARD_SIZE
        self.grid = [[EMPTY for _ in range(self.size)] for _ in range(self.size)]

    def in_bounds(self, r, c):
        return 0 <= r < self.size and 0 <= c < self.size

    def print(self, show_ships=True):
        print("   " + " ".join(str(i) for i in range(self.size)))
        for r in range(self.size):
            row_label = string.ascii_uppercase[r]
            row_str = []
            for c in range(self.size):
                cell = self.grid[r][c]
                if not show_ships and cell == SHIP:
                    row_str.append(EMPTY)
                else:
                    row_str.append(cell)
            print(f"{row_label}  " + " ".join(row_str))
        print()

    def can_place_ship(self, r, c, length, orientation):
        if orientation == 'H':
            if c + length > self.size:
                return False
            for i in range(length):
                if self.grid[r][c + i] != EMPTY:
                    return False
        else:
            if r + length > self.size:
                return False
            for i in range(length):
                if self.grid[r + i][c] != EMPTY:
                    return False
        return True

    def place_ship(self, r, c, length, orientation):
        if orientation == 'H':
            for i in range(length):
                self.grid[r][c + i] = SHIP
        else:
            for i in range(length):
                self.grid[r + i][c] = SHIP

    def random_place_ships(self, shipsizes):
        used_rows = set()
        used_cols = set()

        for length in shipsizes:
            placed = False
            attempts = 0

            while not placed:
                attempts += 1
                if attempts > 1000:
                    # fallback: relax constraint if board becomes too constrained
                    used_rows.clear()
                    used_cols.clear()

                r = random.randint(0, self.size - 1)
                c = random.randint(0, self.size - 1)
                orientation = random.choice(['H', 'V'])

                # ---- row/column separation constraint ----
                if orientation == 'H':
                    if r in used_rows:
                        continue
                else:  # 'V'
                    if c in used_cols:
                        continue

                if self.can_place_ship(r, c, length, orientation):
                    self.place_ship(r, c, length, orientation)
                    placed = True

                    # ---- mark occupied rows / columns ----
                    if orientation == 'H':
                        used_rows.add(r)
                        for i in range(length):
                            used_cols.add(c + i)
                    else:
                        used_cols.add(c)
                        for i in range(length):
                            used_rows.add(r + i)

    def all_ships_sunk(self):
        for r in range(self.size):
            for c in range(self.size):
                if self.grid[r][c] == SHIP:
                    return False
        return True

    def receive_shot(self, r, c):
        if not self.in_bounds(r, c):
            return "OUT"
        cell = self.grid[r][c]
        if cell == SHIP:
            self.grid[r][c] = HIT
            return "HIT"
        elif cell == EMPTY:
            self.grid[r][c] = MISS
            return "MISS"
        else:
            return "REPEAT"
