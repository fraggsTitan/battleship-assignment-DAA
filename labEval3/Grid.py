from Fleet import Fleet
from functools import lru_cache
from UnplacableShipException import UnplacableShipException
import random
from typing import List, Tuple, Set, Dict
from enum import Enum
from Sorting import insertionSortByIndex,insertionSortDescending
class Grid:
    """
        THARUN-CB.SC.U4CSE24053
    """
    #role defines if user is ai or player
    class Role(Enum):
        PLAYER=0
        AI=1
    #can raise this exception when invalid role tries to perform another roles operation
    class RoleException(Exception):
        pass
    def __init__(self,size:int,shipLengths:list[int],role:Role):#user gives grid size and ship size
        if(any(ship>size for ship in shipLengths)):
            raise UnplacableShipException(f"Fleet cannot be made as not every one of  ships( Biggest with size: {max(shipLengths)}) fits into the board  of size {size}")
        self.fleet = Fleet(size)
        self.shipLengths=insertionSortDescending(shipLengths.copy())
        self.role=role
        self.shipCells=set()#stores all hit cells which hit a ship
    
    def isPlacementValid(self, vertices):
        for v in vertices:
            if self.fleet.cellOccupied(v):
                return False
        return True
    

    #can periodically check for this from frontend after every move
    def allShipsSunk(self):
        return len(self.shipLengths)==0


    #--REMOVE
    def placeAllShips(self):
        """
        Backtracking based full fleet placement.
        Randomized search order for different board layouts each run.
        """
        success = self.placeShipsBacktracking()

        if not success:
            raise UnplacableShipException(
                f"All ships couldn't be placed: {self.shipLengths}"
            )

        # Fix aliveShips count properly after placement
        self.fleet.aliveShips = len(self.fleet.ships)
    def placeShipsBacktracking(self):
        self._blocked = [[0]*self.fleet.sideLength for _ in range(self.fleet.sideLength)]
        ships = list(self.shipLengths)
        random.shuffle(ships)   # randomness in order
        return self._placeHelper(ships, 0)
        
    def _placeHelper(self, ships, index):
        if index == len(ships):
            return True

        size = self.fleet.sideLength
        length = ships[index]

        positions = [(r, c) for r in range(size) for c in range(size)]
        random.shuffle(positions)

        orientations = [True, False]
        random.shuffle(orientations)

        for horizontal in orientations:
            for (row, col) in positions:

                if self.can_place_shipAI(row, col, length, horizontal):

                    vertices = self._getVertices(row, col, length, horizontal)

                    # Place
                    self.fleet.addShip(vertices)
                    self._markShip(vertices, +1)

                    if self._placeHelper(ships, index + 1):
                        return True

                    # Backtrack
                    self._markShip(vertices, -1)
                    self.fleet.removeShip(vertices)

        return False
    def _markShip(self, vertices, delta):
        size = self.fleet.sideLength

        for (r, c) in vertices:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr = r + dr
                    nc = c + dc
                    if 0 <= nr < size and 0 <= nc < size:
                        self._blocked[nr][nc] += delta

    def _getVertices(self, row, col, length, horizontal):
        vertices = []

        if horizontal:
            for i in range(length):
                vertices.append((row, col+i))
        else:
            for i in range(length):
                vertices.append((row+i, col))

    def can_place_shipAI(self, row:int, col:int, length:int, horizontal:bool):
        size = self.fleet.sideLength

        if horizontal:
            if col + length > size:
                return False
            for i in range(length):
                if self._blocked[row][col+i] > 0:
                    return False
        else:
            if row + length > size:
                return False
            for i in range(length):
                if self._blocked[row+i][col] > 0:
                    return False

        return True        
    def can_place_ship(self,r:int,c:int,length:int,orient:chr)->bool:
        #orient can be 'H' or 'V'
        if orient=='H':#horizontal placement
            if(c+length-1>=self.fleet.sideLength):#if the column index exceeds the board length, can't place
                return False
            for i in range(length):
                if(self.fleet.cellOccupied((r,c+i))):
                    return False
            return True
        else:#vertical placement
            if(r+length-1>=self.fleet.sideLength):#if the row index exceeds the board length, can't place
                return False
            for i in range(length):
                if(self.fleet.cellOccupied((r+i,c))):
                    return False
            return True
    
    def player_place_ship(self, r:int, c:int, length:int, orient:chr):
        #frontend only calls this if canplaceship is true
        vertices=set()
        if orient=='H':#horizontal orientation
            for i in range(length):
                vertices.add((r,c+i))
        else:#vertical orientation
            for i in range(length):
                vertices.add((r+i,c))
        self.fleet.addShip(vertices)
        print("Placed ship at vertices: ",vertices)


    """
    Darshan V -CB.SC.U4CSE24009
    """

    #hitting for player
    def playerHit(self,coordinate:Tuple[int,int]):
        print("Player ships:",self.shipLengths)
        if(self.role!=self.Role.PLAYER):
            raise self.RoleException("Cannot call playerHit() unless you have role of PLAYER")
        if coordinate in self.fleet.hitCells:#duplicate cell has been hit
            return None
        return self.makeHit(coordinate)
    #since logic for makeHit is same for AI and PLAYER, we can use  common method for update logic
    def makeHit(self,choice:Tuple[int,int])->Fleet.HitRecord:
        record=self.fleet.hitShip(choice)#hitrecord is generated
        if record.sunk:#if ship was sunk
            self.shipLengths.remove(len(record.ship.cells))#removes that ship from our shiplength array
            for r,c in record.ship.cells:
                if (r,c) in self.shipCells:
                    self.shipCells.remove((r,c))#remove all coordinates of that ship from shipcells
        elif record.hit:#if ship was hit, we just need to add it to shipcells
            self.shipCells.add(choice)
        #frontend can make sense of this record now 
        return record
    
    #DP method to hit ships only when Mode is HUNT
    def huntMode(self)->Tuple[int,int]:
        """
        Maintain 2 2D matrices, one for max number of cells we can extend downwards from a cell and another for max we can extend
        rightwards,  then use this to  build ship count at each cell      
        TC:O(n^2*maxShipSize)
        Space=O(n^2)  
        """
        sideLength=self.fleet.sideLength
        maxShipSize=max(self.shipLengths)#try to find wherever biggest current alive ship can fit
        rightExtension=[[0 for _ in range(sideLength+1)] for _ in range(sideLength+1)]#max cells we can extend in right from current cell
        downExtension=[[0 for _ in range(sideLength+1)] for _ in range(sideLength+1)]#max cells we can extend downwards from current cell
        for i in reversed(range(sideLength)):#iterate from bottom right in right to left fashion and build right and down extension
            for j in reversed(range(sideLength)):
                if(self.fleet.cellHit((i,j))):
                    continue
                rightExtension[i][j]=rightExtension[i][j+1]+1
                downExtension[i][j]=downExtension[i+1][j]+1
        shipCounts=[[0 for _ in range(sideLength)] for _ in range(sideLength)]#store how many possible ships could be placed in a given cell
        for i in range(sideLength):#iterate over all cells and build the shipCounts matrix
            for j in range(sideLength):
                if self.fleet.cellHit((i,j)):
                    continue
                if(rightExtension[i][j]>=maxShipSize):#increase ship counts of all cells where a ship starting from current index could be placed only if the extension value of current cell is at least as large as maxShipSize
                    for k in range(maxShipSize):
                        shipCounts[i][j+k]+=1
                if(downExtension[i][j]>=maxShipSize):
                    for k in range(maxShipSize):
                        shipCounts[i+k][j]+=1
        maxCount = max(max(row) for row in shipCounts)#this is the max shipcount in any cell over all the cells
        maxCells = [
                (i, j)
                for i in range(sideLength)
                for j in range(sideLength)
                if shipCounts[i][j] == maxCount
            ]#all cells with shipcount==maxcount
        return random.choice(maxCells)#pick random cell from maxcells
    
    
    def _getAllClusters(self):
        visited = set()
        clusters = []

        for cell in self.shipCells:
            if cell in visited:
                continue

            stack = [cell]
            component = set()

            while stack:
                curr = stack.pop()
                if curr in visited:
                    continue

                visited.add(curr)
                component.add(curr)

                r, c = curr
                neighbors = [(r+1,c),(r-1,c),(r,c+1),(r,c-1)]
                for n in neighbors:
                    if n in self.shipCells and n not in visited:
                        stack.append(n)

            clusters.append(component)

        return clusters
    #--add
    #modify
    def targetMode(self) -> Tuple[int, int]:
        size = self.fleet.sideLength
        clusters = self._getAllClusters()

        # Resolve larger clusters first
        clusters.sort(key=len, reverse=True)

        for cluster in clusters:

            hits = list(cluster)

            # ---------- CASE 1: Single Hit ----------
            if len(hits) == 1:
                r, c = hits[0]
                neighbors = [(r+1,c),(r-1,c),(r,c+1),(r,c-1)]

                valid = [
                    (nr,nc)
                    for (nr,nc) in neighbors
                    if 0 <= nr < size and 0 <= nc < size
                    and not self.fleet.cellHit((nr,nc))
                ]

                if valid:
                    return random.choice(valid)

            # ---------- CASE 2: Multiple Hits ----------
            rows = {r for r,_ in hits}
            cols = {c for _,c in hits}

            # --------- ORIENTATION LOCKED ----------
            if len(rows) == 1:  # Horizontal
                row = next(iter(rows))
                sorted_hits = sorted(hits, key=lambda x: x[1])
                left = sorted_hits[0][1]
                right = sorted_hits[-1][1]

                candidates = [
                    (row, left-1),
                    (row, right+1)
                ]

            elif len(cols) == 1:  # Vertical
                col = next(iter(cols))
                sorted_hits = sorted(hits, key=lambda x: x[0])
                top = sorted_hits[0][0]
                bottom = sorted_hits[-1][0]

                candidates = [
                    (top-1, col),
                    (bottom+1, col)
                ]

            # --------- AMBIGUOUS (L SHAPE OR TOUCHING SHIPS) ----------
            else:
                candidates = []
                for (r,c) in hits:
                    neighbors = [(r+1,c),(r-1,c),(r,c+1),(r,c-1)]
                    for cell in neighbors:
                        if cell not in cluster:
                            candidates.append(cell)

            # ---------- FILTER VALID ----------
            valid = [
                (r,c)
                for (r,c) in candidates
                if 0 <= r < size and 0 <= c < size
                and not self.fleet.cellHit((r,c))
            ]

            if valid:
                return random.choice(valid)

            # ---------- BACKTRACK STEP ----------
            # If orientation guessed but ends blocked,
            # try all adjacent cells of cluster

            expanded = []
            for (r,c) in hits:
                neighbors = [(r+1,c),(r-1,c),(r,c+1),(r,c-1)]
                for cell in neighbors:
                    if cell not in cluster:
                        expanded.append(cell)

            valid = [
                (r,c)
                for (r,c) in expanded
                if 0 <= r < size and 0 <= c < size
                and not self.fleet.cellHit((r,c))
            ]

            if valid:
                return random.choice(valid)

        # If no cluster produced move (should not happen)
        raise Exception("Target mode failed to find adjacent extension.")
        
    
    #THIS METHOD COMMUNICATES WITH FRONTEND SO MAKE INFORMATION VERY CLEAR
    def getHit(self)->Tuple[int,int]:
        print("AI ships:",self.shipLengths)
        if(self.role!=self.Role.AI):
            raise self.RoleException("Cannot call getHit() unless you have role of AI")
        #gets a hit coordinate and then launches hit on that cell
        if len(self.shipCells)>0:#target mode
            choice=self.targetMode()
        else:
            choice=self.huntMode()
        return choice




