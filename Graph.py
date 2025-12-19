from States import CellState, AIModeS


class Graph:

    class Cell:
        def __init__(self, i, j):
            self.i = i
            self.j = j
            self.state = CellState.UNKNOWN

        def set_state(self, state):
            self.state = state
