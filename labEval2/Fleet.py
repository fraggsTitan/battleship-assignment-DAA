from ConflictingCoordinateException import ConflictingCoordinateException
from Ship import Ship
from OutOfBoundsException import OutOfBoundsException

class Fleet:

    def __init__(self,sideLength):
        self.ships=set()#set of ships
        self.nodes={}#dictionary of nodes mapping to ships
        self.hitCells=set()#maintain record of every single cell which has been hit
        self.aliveShips=0
        self.sideLength=sideLength

    def addShip(self,vertices):#array of coordinates to represent a ship
        for coordinate in vertices:
            if(coordinate in self.nodes):
                raise ConflictingCoordinateException(f"The coordinate {coordinate} has already been used by another ship of size {len(self.nodes.get(coordinate).cells)}")
            if(self.outOfBounds(coordinate)):
                raise OutOfBoundsException(f"The cell {coordinate} in {vertices} is out of bounds for a {self.sideLength}x{self.sideLength} grid.")
        newShip=Ship(vertices)
        self.ships.add(newShip)
        self.aliveShips=self.aliveShips+1

        for coordinate in newShip.cells:
            self.nodes[coordinate]=newShip
        

    def hitShip(self,coordinate):#orchestrates a hit 
        if(self.outOfBounds(coordinate)):
                raise OutOfBoundsException(f"The cell {coordinate}is out of bounds for a {self.sideLength}x{self.sideLength} grid.")
        if coordinate in self.hitCells:
            raise ConflictingCoordinateException(f"This cell,{coordinate},has already been hit. Hit another cell")
        
        self.hitCells.add(coordinate)

        if coordinate not in self.nodes:
            return self.HitRecord(hit=False,sunk=False,ship=None)#ship not hit and ship not killed so no ship returned
        
        targetShip=self.nodes[coordinate]#ship being targeted right now
        targetShip.lives=targetShip.lives-1
        if targetShip.lives==0:#
            self.aliveShips=self.aliveShips-1#ship is dead
            return self.HitRecord(hit=True,sunk=True,ship=targetShip)#return target ship for UI to mark as killed       
        return self.HitRecord(hit=True,sunk=False,ship=None)#cell was hit but ship not killed
    
    def outOfBounds(self, coordinate):
        r, c = coordinate
        return not (0 <= r < self.sideLength and 0 <= c < self.sideLength)
    
    def fleetAlive(self):#returns if fleet is alive or not
        return self.aliveShips>0
    
    def cellOccupied(self,coordinate):
        return coordinate in self.nodes

    class HitRecord:

        def __init__(self,hit,sunk,ship):
            self.hit=hit
            self.sunk=sunk
            self.ship=ship
    def __str__(self):
        lines = []

        for r in range(self.sideLength):
            row = []
            for c in range(self.sideLength):
                coord = (r, c)

                if coord in self.hitCells:
                    if coord in self.nodes:
                        row.append("X")  # hit ship
                    else:
                        row.append("o")  # miss
                else:
                    if coord in self.nodes:
                        row.append("S")  # ship not hit
                    else:
                        row.append(".")  # empty water

            lines.append(" ".join(row))

        return "\n".join(lines)

