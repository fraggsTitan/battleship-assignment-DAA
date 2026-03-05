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
    def placeAllShips(self):#no return
        #uses shipDAC and places all ships
        for i in range(len(self.shipLengths)):
            ship=self.shipLengths[i]
            result=self.shipDAC(0,0,self.fleet.sideLength-1,self.fleet.sideLength-1,ship)#returns a vertex set
            if (result is None):
                raise UnplacableShipException(f"All ships couldn't be placed: (Issue encountered on ship at index {i} in {self.shipLengths})")
            placing=result[0]
            self.fleet.addShip(placing)
        #will place all ships

        
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
    #REMOVE
    def dfs(self):
        seed = next(iter(self.shipCells))
        stack = [seed]
        cluster = set()

        while stack:
            cell = stack.pop()
            if cell in cluster:
                continue
            cluster.add(cell)

            i, j = cell
            neighbors = [(i+1,j),(i-1,j),(i,j+1),(i,j-1)]
            for n in neighbors:
                if n in self.shipCells and n not in cluster:
                    stack.append(n)
        return cluster
    
    def targetMode(self) -> Tuple[int, int]:
        sideLength = self.fleet.sideLength

        # ---- Step 1: Extract ONE connected cluster ----
        cluster=self.dfs()

        hits = list(cluster)

        candidates = []

        # ---- Step 2: Single hit case ----
        if len(hits) == 1:
            i, j = hits[0]
            neighbors = [(i+1,j),(i-1,j),(i,j+1),(i,j-1)]
            candidates.extend(neighbors)

        else:
            rows = {i for i,_ in hits}
            cols = {j for _,j in hits}

            # Horizontal
            if len(rows) == 1:
                row = next(iter(rows))
                sorted_hits = sorted(hits, key=lambda x: x[1])
                minCol = sorted_hits[0][1]
                maxCol = sorted_hits[-1][1]

                candidates.append((row, minCol - 1))
                candidates.append((row, maxCol + 1))

            # Vertical
            elif len(cols) == 1:
                col = next(iter(cols))
                sorted_hits = sorted(hits, key=lambda x: x[0])
                minRow = sorted_hits[0][0]
                maxRow = sorted_hits[-1][0]

                candidates.append((minRow - 1, col))
                candidates.append((maxRow + 1, col))

            # Weird shape (inconsistent cluster)
            else:
                for i,j in hits:
                    neighbors = [(i+1,j),(i-1,j),(i,j+1),(i,j-1)]
                    candidates.extend(neighbors)

        # ---- Step 3: Filter valid candidates ----
        valid = [
            (x,y)
            for (x,y) in candidates
            if 0 <= x < sideLength
            and 0 <= y < sideLength
            and not self.fleet.cellHit((x,y))
        ]

        # ---- Step 4: If no direct extension works ----
        if not valid:
            # Expand search around cluster more aggressively
            expanded = []
            for i,j in cluster:
                neighbors = [
                    (i+1,j),(i-1,j),(i,j+1),(i,j-1),
                    (i+1,j+1),(i+1,j-1),(i-1,j+1),(i-1,j-1)
                ]
                expanded.extend(neighbors)

            valid = [
                (x,y)
                for (x,y) in expanded
                if 0 <= x < sideLength
                and 0 <= y < sideLength
                and not self.fleet.cellHit((x,y))
            ]

        # ---- Final Safety: GUARANTEED return inside target mode ----
        if not valid:
            # Last resort: pick any unhit cell adjacent to cluster region
            for i in range(sideLength):
                for j in range(sideLength):
                    if not self.fleet.cellHit((i,j)):
                        return (i,j)

        return random.choice(valid)
        
    
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




