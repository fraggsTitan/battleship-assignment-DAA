# Graph.py
import random
from enum import Enum


class Cell(Enum):
    EMPTY = 0
    SHIP = 1
    HIT = 2
    MISS = 3


class Board:
    def __init__(self, size=10):
        self.size = size
        self.grid = [[Cell.EMPTY for _ in range(size)] for _ in range(size)]
        # ship_id -> list[(r, c)]
        self.ships = {}
        self.ship_id_counter = 0

    def in_bounds(self, r, c):
        return 0 <= r < self.size and 0 <= c < self.size

    def place_ship_random(self, length):
        """
        Random ship placement:
        pick random (r, c, horizontal/vertical) until a non‑overlapping,
        in‑bounds path of given length is found, then mark as SHIP.
        """
        while True:
            r = random.randint(0, self.size - 1)
            c = random.randint(0, self.size - 1)
            horizontal = random.choice([True, False])

            cells = []
            ok = True
            for i in range(length):
                nr = r
                nc = c
                if horizontal:
                    nc = c + i
                else:
                    nr = r + i

                if not self.in_bounds(nr, nc):
                    ok = False
                    break
                if self.grid[nr][nc] != Cell.EMPTY:
                    ok = False
                    break
                cells.append((nr, nc))

            if not ok:
                continue

            ship_id = self.ship_id_counter
            self.ship_id_counter += 1
            self.ships[ship_id] = cells
            for (nr, nc) in cells:
                self.grid[nr][nc] = Cell.SHIP
            return ship_id

    def receive_shot(self, r, c):
        """
        Apply a shot to this board.
        Returns: "MISS", "HIT", "SUNK", "REPEAT", "OUT"
        """
        if not self.in_bounds(r, c):
            return "OUT"

        cell = self.grid[r][c]
        if cell in (Cell.HIT, Cell.MISS):
            return "REPEAT"

        if cell == Cell.EMPTY:
            self.grid[r][c] = Cell.MISS
            return "MISS"

        if cell == Cell.SHIP:
            self.grid[r][c] = Cell.HIT
            # find which ship and check sunk
            for ship_id, cells in self.ships.items():
                if (r, c) in cells:
                    if all(self.grid[rr][cc] == Cell.HIT for (rr, cc) in cells):
                        return "SUNK"
                    return "HIT"

        return "MISS"

    def all_sunk(self):
        for cells in self.ships.values():
            for (r, c) in cells:
                if self.grid[r][c] == Cell.SHIP:
                    return False
        return True

    def debug_print(self, reveal=False):
        """
        Simple text output for debugging.
        """
        for r in range(self.size):
            row = []
            for c in range(self.size):
                cell = self.grid[r][c]
                if cell == Cell.EMPTY:
                    ch = "."
                elif cell == Cell.SHIP:
                    ch = "S" if reveal else "."
                elif cell == Cell.HIT:
                    ch = "X"
                elif cell == Cell.MISS:
                    ch = "o"
                else:
                    ch = "?"
                row.append(ch)
            print(" ".join(row))
        print()
