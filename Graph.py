# graph.py

class Vertex:
    def __init__(self, r, c):
        self.r = r
        self.c = c

    def __hash__(self):
        return hash((self.r, self.c))

    def __eq__(self, other):
        return self.r == other.r and self.c == other.c

    def __repr__(self):
        return f"V({self.r},{self.c})"


class GridGraph:
    """
    Explicit graph representation of a BOARD_SIZE x BOARD_SIZE grid.
    Vertices are cells, edges are 4-directional adjacency.
    """

    def __init__(self, board):
        self.board = board
        self.size = board.size

    def neighbors(self, v: Vertex):
        """
        GRAPH ADJACENCY:
        Returns all adjacent vertices (edges implied).
        """
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        result = []

        for dr, dc in directions:
            nr, nc = v.r + dr, v.c + dc
            if 0 <= nr < self.size and 0 <= nc < self.size:
                result.append(Vertex(nr, nc))

        return result

"""
Try to represent nodes as edges of graph, we can have 2 types of nodes:
1. Missed Nodes
2. Hit Nodes
anything else, we don't have to care about

in each placed component, we have to model a ship as a continuous segment of such nodes,
maybe in each of the boards we just store the indexes of the ship
we can have it like
dictionary of each ship vertex pointing to a ship,
array of such ships are maintained, when you hit, you can remove it from this list and add it to the corresponding players hit board.
when an array size becomes 0, ship is dead,send a notification to user

"""