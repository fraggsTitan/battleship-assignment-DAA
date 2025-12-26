# graph.py

# Why needed: Instead of using tuples (r,c) everywhere, Vertex objects are more readable and have special methods (next functions) for graphs.
#"Each board cell is represented as a Vertex(r,c) object so the AI can treat hits as graph nodes during DFS."

# Implemented __hash__ and __eq__ so Vertex objects are hashable. This lets AI use sets for tried shots and DFS visited tracking. Hash of (r,c) tuple ensures same position = same hash + equality.

class Vertex:
    def __init__(self, r, c):
        self.r = r
        self.c = c

    def __hash__(self): #Why needed: Sets use hash values to quickly find/store objects. Same position = same hash.
        return hash((self.r, self.c))

    def __eq__(self, other):
        return self.r == other.r and self.c == other.c

    def __repr__(self):
        return f"V({self.r},{self.c})"


class GridGraph:
    """
    Explicit graph representation of a BOARD_SIZE x BOARD_SIZE grid.
    Vertices are cells, edges are 4-directional adjacency.
    Used by AI for DFS traversal of HIT components.
    """
    #GridGraph wraps a Board object. Stores it directly so neighbors() can read self.board.grid[r][c] to check hits.
    def __init__(self, board): #Why needed: Board is needed to know grid size and cell states during neighbor checks.
        self.board = board
        self.size = board.size

    def neighbors(self, v: Vertex): #returns list of adjacent Vertex objects. Called by AI during DFS.
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
    # Why needed: AI uses GridGraph to find connected HIT cells during target mode.
    # Explicit graph adjacency. AI calls graph.neighbors(hit_vertex) during DFS to find connected hit components.