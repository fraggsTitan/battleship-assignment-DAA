from States import CellState,AIModeS
class Graph:
    class Cell:
        i=0
        j=0 
        state=CellState.UNKNOWN
        def __init__(self,i,j):
            self.i=i
            self.j=j
        def setState(state):
            self.state=state

        
