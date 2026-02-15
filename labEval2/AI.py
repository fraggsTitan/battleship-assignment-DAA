from Fleet import Fleet
from functools import lru_cache

class AI:
    def __init__(self,size):
        self.fleet = Fleet(10)

    def place_ships(self):
        placements = place_ships_dp(self.fleet.sideLength)
        for shipCells in placements:
            self.fleet.addShip(shipCells)

def plan_ship_layout(sideLength):
    ships = [5,4,3,2,1]

    @lru_cache(None)
    def dp(i, rows, cols):
        if i == len(ships):
            return max(rows) + max(cols), []

        best = (float('inf'), None)
        k = ships[i]

        rows = list(rows)
        cols = list(cols)

        # try horizontal in each row
        for r in range(sideLength):
            newRows = rows[:]
            newCols = cols[:]
            newRows[r] += k
            for c in range(k):
                newCols[c] += 1

            score, plan = dp(i+1, tuple(newRows), tuple(newCols))
            if score < best[0]:
                best = (score, [("H", r, k)] + plan)

        # try vertical in each column
        for c in range(sideLength):
            newRows = rows[:]
            newCols = cols[:]
            newCols[c] += k
            for r in range(k):
                newRows[r] += 1

            score, plan = dp(i+1, tuple(newRows), tuple(newCols))
            if score < best[0]:
                best = (score, [("V", c, k)] + plan)

        return best

    _, plan = dp(0, tuple([0]*sideLength), tuple([0]*sideLength))
    return plan

ai = AI()
ai.place_ships()
print(ai.fleet)
