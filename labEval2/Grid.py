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
    

    #can periodically check for this from frontend after every move
    def allShipsSunk(self):
        return len(self.shipLengths)==0







