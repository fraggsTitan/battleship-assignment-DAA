from States import CellState, AIModeS

class Graph:

    class Cell:
        def __init__(self, i, j):
            self.i = i
            self.j = j
            self.state = CellState.UNKNOWN

        def set_state(self, state):
            self.state = state
    def __init__(self):
        self.grid=[[]]
        grid=10*[]
        for i in range(10):
            grid[i]=10*[]
            for j in range (10):
                grid[i][j]=Graph.Cell(i,j)

    def setHit(self,i,j,state):
        if(i>=10 or j>=10):
            IndexError("Illegal index")
        self.grid[i][j].set_state(state)
    
            