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
    """
        Plan:
        For placement use DAC, for each ship, call  a DAC function that recursively divides board into subregions and
        places ship in a region with minimum other ships

        For hitting use DP, something like tracing a path from top-left to bottom right in a grid in terms of DP
    """
    #bottom and rightbound are magnitude values, not actual values w.r.t the grid
    #TC:0(n2) SC:0(1) extra
    def regionOccupancy(self,startI:int,startJ:int,rightBound:int,bottomBound:int)->int:
        #iterate over all coordinates and return how many cells in region are occupied
        shipsInRegion=0
        for i in range(startI,startI+bottomBound+1):
            for j in range(startJ,startJ+rightBound+1):
                if(self.fleet.cellOccupied((i,j))):
                    shipsInRegion=shipsInRegion+1
        return shipsInRegion
    
    def isPlacementValid(self, vertices):
        for v in vertices:
            if self.fleet.cellOccupied(v):
                return False
        return True
    
    #TC : O(1)
    #can periodically check for this from frontend after every move
    def allShipsSunk(self):
        return len(self.shipLengths)==0

    """
        Vishnu- CB.SC.U4CSE24060
    """

    def generateRandomVerticesForShip(self,startI:int,startJ:int,rightBound:int,bottomBound:int,shipSize:int)->Set[Tuple[int,int]]:# This function is O(k) where k is shipSize
        #starti,startj specify a unique region in the fleet grid, this should be such that that region has 0 other ships
        #it must also be guaranteed that the ship of given size can actually fit in this region
        #right bound,bottomBound are inclusive
        isHorizontal=True if random.randint(0,1)==0 else False #randomly choose orientation
        if(shipSize>bottomBound+1):#for eg if ship size is 3 and bottom bound is 1 then only 2 vertical cells available
            #must place horizontally
            isHorizontal=True
        elif(shipSize>rightBound+1):
            isHorizontal=False
        if(isHorizontal):
            #place ship horizontally pick random i, then extend ship from there
            randomI = random.randint(startI, startI + bottomBound)
            randomJ = random.randint(startJ, startJ + rightBound - shipSize + 1)
            if(randomI>11 or randomJ>11):
                print(f"Function call for incorrect params is : {startI},{startJ},{rightBound},{bottomBound},{shipSize}")
            vertices=set()
            for j in range(shipSize):
                vertices.add((randomI, randomJ + j))
        else:#place ship vertically, pick random j and extend from there
            randomI = random.randint(startI, startI + bottomBound - shipSize + 1)
            randomJ = random.randint(startJ, startJ + rightBound)
            if(randomI>11 or randomJ>11):
                print(f"Function call for incorrect params is : {startI},{startJ},{rightBound},{bottomBound},{shipSize}")
            vertices=set()
            for i in range(shipSize):
                vertices.add((randomI + i, randomJ))
        return vertices
    #TC: O(n2logn) SC:O(logn)
    #this function recursively does DAC to fit in ship, this only returns vertices where to place ship, actual ship placement 
    #has to be elsewhere
    def shipDAC(self,startI:int,startJ:int,rightBound:int,bottomBound:int,shipSize:int)->Tuple[Set[Tuple[int,int]],int]:
        #returns a tuple consisting of:
        #   a.set of tuples that points to random vertices generated 
        #   b. how many ship cells in that region are taken
        if startI+shipSize>=self.fleet.sideLength and startJ+shipSize>=self.fleet.sideLength:
            return None
        if startI+bottomBound>=self.fleet.sideLength or startJ+rightBound>=self.fleet.sideLength:
            return None
        if rightBound < 0 or bottomBound < 0:
            return None
        if((shipSize>bottomBound+1)and(shipSize>rightBound+1)):
            #ship cannot be placed here
            return None#no ordering of vertices can be generated as area is too small
        if(self.regionOccupancy(startI,startJ,rightBound,bottomBound)==0):
            #if region is unooccupied, place ship randomly in it
            vertices=self.generateRandomVerticesForShip(startI,startJ,rightBound,bottomBound,shipSize)
            assert self.isPlacementValid(vertices), "Generated placement overlaps!"#assert that the  value is always non-overlapping, if there is some edge case missed 
            return (vertices,0)#will always be valid since region occupancy is 0
        
        #DIVIDE
        topLeft=self.shipDAC(startI,startJ,rightBound//2,bottomBound//2,shipSize)
        topRight=self.shipDAC(startI,startJ+rightBound//2+1,rightBound//2,bottomBound//2,shipSize)
        bottomLeft=self.shipDAC(startI+bottomBound//2+1,startJ,rightBound//2,bottomBound//2,shipSize)
        bottomRight=self.shipDAC(startI+bottomBound//2+1,startJ+rightBound//2+1,rightBound//2,bottomBound//2,shipSize)

        #CONQUER
        if((topLeft is None) and (topRight is None) and (bottomLeft is None) and (bottomRight is None)):
            #our divide didn't return valid region so do bruteforce and if possible find a placement
            print(f"Brute force placement generated for region start at {startI},{startJ}, bounds: {rightBound},{bottomBound}")
            return self.bruteForcePlacement(startI,startJ,rightBound,bottomBound,shipSize)
        minOccupied=1000000000000#random large number since infinity can't be used with int
        for region in [topLeft,topRight,bottomLeft,bottomRight]:
            if region is None:
                continue
            minOccupied=min(minOccupied,region[1])#get region with min ships
        minShipRegions=[region for region in [topLeft,topRight,bottomLeft,bottomRight] if region is not None and region[1]==minOccupied]
        return (minShipRegions[random.randint(0,len(minShipRegions)-1)][0],self.regionOccupancy(startI,startJ,rightBound,bottomBound))

    #O(n2)
    def bruteForcePlacement(self, startI, startJ, rightBound, bottomBound, shipSize):
        endI = startI + bottomBound
        endJ = startJ + rightBound

        # Try horizontal placements
        for i in range(startI, endI + 1):
            for j in range(startJ, endJ - shipSize + 2):
                vertices = {(i, j + k) for k in range(shipSize)}
                if i> 11 or j> 11:
                    print(f"Function call for incorrect params is : {startI},{startJ},{rightBound},{bottomBound},{shipSize}")
                if self.isPlacementValid(vertices):
                    return (vertices, self.regionOccupancy(startI, startJ, rightBound, bottomBound))

        # Try vertical placements
        for i in range(startI, endI - shipSize + 2):
            for j in range(startJ, endJ + 1):
                vertices = {(i + k, j) for k in range(shipSize)}
                if i> 11 or j> 11:
                    print(f"Function call for incorrect params is : {startI},{startJ},{rightBound},{bottomBound},{shipSize}")
                if self.isPlacementValid(vertices):
                    return (vertices, self.regionOccupancy(startI, startJ, rightBound, bottomBound))

        return None

    
    #O(k*n2logn)
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

    #O(k)
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
    #O(k)
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
    
    def targetMode(self) -> Tuple[int, int]:
        sideLength = self.fleet.sideLength

        # ---- Step 1: get one connected cluster ----
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

        hits = list(cluster)

        # ---- Step 2: single hit ----
        if len(hits) == 1:
            i, j = hits[0]
            neighbors = [(i+1,j),(i-1,j),(i,j+1),(i,j-1)]

            valid = [
                (x,y)
                for (x,y) in neighbors
                if 0 <= x < sideLength
                and 0 <= y < sideLength
                and not self.fleet.cellHit((x,y))
            ]

            return random.choice(valid)

        # ---- Step 3: determine orientation safely ----
        rows = {i for i,_ in hits}
        cols = {j for _,j in hits}

        candidates = []

        if len(rows) == 1:  # horizontal
            row = next(iter(rows))
            sorted_hits = insertionSortByIndex(hits.copy(), 1)
            minCol = sorted_hits[0][1]
            maxCol = sorted_hits[-1][1]

            candidates = [
                (row, minCol - 1),
                (row, maxCol + 1)
            ]

        elif len(cols) == 1:  # vertical
            col = next(iter(cols))
            sorted_hits = insertionSortByIndex(hits.copy(), 0)
            minRow = sorted_hits[0][0]
            maxRow = sorted_hits[-1][0]

            candidates = [
                (minRow - 1, col),
                (maxRow + 1, col)
            ]

        else:
            # ambiguous (touching ships forming non-line shape)
            for i,j in hits:
                for n in [(i+1,j),(i-1,j),(i,j+1),(i,j-1)]:
                    if n not in cluster:
                        candidates.append(n)

        valid = [
            (x,y)
            for (x,y) in candidates
            if 0 <= x < sideLength
            and 0 <= y < sideLength
            and not self.fleet.cellHit((x,y))
        ]

        # At this point, valid SHOULD exist if ship not resolved.
        # If not, something outside targetMode should clear cluster.
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




