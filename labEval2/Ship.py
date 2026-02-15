class Ship:
    
    def __init__(self,vertices):#vertices is a array of cells to which this ship begins
        self.cells=set(vertices)#set of vertices
        self.lives=len(vertices)#how many lifes this ship has left

    def __repr__(self):
        return f"{self.cells}"