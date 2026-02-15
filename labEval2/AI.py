from Fleet import Fleet
from functools import lru_cache
from UnplacableShipException import UnplacableShipException
class AI:
    def __init__(self,size,shipLengths):#user gives grid size and ship size
        if(any(ship>size for ship in shipLengths)):
            raise UnplacableShipException(f"Fleet cannot be made as not every one of  ships( Biggest with size: {max(shipLengths)}) fits into the board  of size {size}")
        self.fleet = Fleet(12)
        

    def place_ships(self):
        placements = self.plan_ship_layout()
        self.place_from_plan(placements)
        print(self.fleet)
    def plan_ship_layout(self):
        ships = [5,4,3,2,1]
        memo = {}  # explicit memo table
        sideLength=self.fleet.sideLength
        def dp(i, rows, cols):
            key = (i, rows, cols)

            # ---- MEMO LOOKUP ----
            if key in memo:
                return memo[key]

            # ---- BASE CASE ----
            if i == len(ships):
                result = (max(rows) + max(cols), [])
                memo[key] = result
                return result

            bestScore = float('inf')
            bestPlan = None
            k = ships[i]

            rows_list = list(rows)
            cols_list = list(cols)

            # ---- TRY HORIZONTAL ----
            for r in range(sideLength):
                newRows = rows_list[:]
                newCols = cols_list[:]

                newRows[r] += k
                for c in range(k):
                    newCols[c] += 1

                score, plan = dp(i+1, tuple(newRows), tuple(newCols))

                if score < bestScore:
                    bestScore = score
                    bestPlan = [("H", r, k)] + plan

            # ---- TRY VERTICAL ----
            for c in range(sideLength):
                newRows = rows_list[:]
                newCols = cols_list[:]

                newCols[c] += k
                for r in range(k):
                    newRows[r] += 1

                score, plan = dp(i+1, tuple(newRows), tuple(newCols))

                if score < bestScore:
                    bestScore = score
                    bestPlan = [("V", c, k)] + plan

            result = (bestScore, bestPlan)

            # ---- MEMO STORE ----
            memo[key] = result

            return result

        _, plan = dp(0, tuple([0]*sideLength), tuple([0]*sideLength))
        print("Memoization dict length: ",len(memo))
        return plan

    def place_from_plan(self, plan):
        occupied = set()
        fleet=self.fleet
        for orient, idx, size in plan:
            if orient == "H":
                r = idx
                for c in range(fleet.sideLength):
                    cells = [(r, c+i) for i in range(size)]
                    if all((x,y) not in occupied and c+size <= fleet.sideLength for x,y in cells):
                        for cell in cells:
                            occupied.add(cell)
                        fleet.addShip(cells)
                        break

            else:
                c = idx
                for r in range(fleet.sideLength):
                    cells = [(r+i, c) for i in range(size)]
                    if all((x,y) not in occupied and r+size <= fleet.sideLength for x,y in cells):
                        for cell in cells:
                            occupied.add(cell)
                        fleet.addShip(cells)
                        break


ai=AI(12)
ai.place_ships()
print(ai.fleet)