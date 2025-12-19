# CPU.py
import random
from collections import defaultdict, deque
from Graph import Cell


class CPU:
    """
    CPU AI:
    - Hunt mode: probability map – for each cell, how many ships can pass through it.
    - Target mode: BFS queue of neighbours, but neighbours are added ONLY when
      the *current* shot is a HIT (the 'red cell' rule).
    """

    def __init__(self, board_size=10):
        self.size = board_size
        self.mode = "HUNT"
        self.hunt_prob = defaultdict(int)
        self.hunt_cache = {}          # (r, c, dr, dc, L) -> bool
        self.remaining_ship_lengths = [5, 4, 3, 3, 2]

        # Targeting state
        self.bfs_queue = deque()
        self.visited_target = set()

    # ---------- HUNT MODE ---------- #

    def recompute_hunt_prob(self, enemy_board):
        self.hunt_prob.clear()
        self.hunt_cache.clear()
        ships = self.remaining_ship_lengths
        N = enemy_board.size

        def can_place(r, c, dr, dc, length):
            key = (r, c, dr, dc, length)
            if key in self.hunt_cache:
                return self.hunt_cache[key]
            for i in range(length):
                nr = r + dr * i
                nc = c + dc * i
                if not (0 <= nr < N and 0 <= nc < N):
                    self.hunt_cache[key] = False
                    return False
                # cannot pass through known MISS
                if enemy_board.grid[nr][nc] == Cell.MISS:
                    self.hunt_cache[key] = False
                    return False
            self.hunt_cache[key] = True
            return True

        for r in range(N):
            for c in range(N):
                for L in ships:
                    # horizontal
                    if can_place(r, c, 0, 1, L):
                        for i in range(L):
                            self.hunt_prob[(r, c + i)] += 1
                    # vertical
                    if can_place(r, c, 1, 0, L):
                        for i in range(L):
                            self.hunt_prob[(r + i, c)] += 1

    def choose_hunt_target(self, enemy_board):
        scored = []
        N = enemy_board.size
        for r in range(N):
            for c in range(N):
                cell = enemy_board.grid[r][c]
                if cell in (Cell.HIT, Cell.MISS):
                    continue
                score = self.hunt_prob.get((r, c), 0)
                scored.append((score, r, c))

        if not scored:
            # fallback – pick any unshot
            choices = [
                (r, c)
                for r in range(N)
                for c in range(N)
                if enemy_board.grid[r][c] not in (Cell.HIT, Cell.MISS)
            ]
            return random.choice(choices)

        max_score = max(s for (s, _, _) in scored)
        best_cells = [(r, c) for (s, r, c) in scored if s == max_score]
        return random.choice(best_cells)

    # ---------- TARGET MODE (neighbour‑only BFS) ---------- #

    def _add_neighbours_of_hit(self, r, c, enemy_board):
        """
        Only called when CURRENT shot is HIT.
        Enqueues 4‑direction neighbours that are still unknown.
        """
        dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < enemy_board.size and 0 <= nc < enemy_board.size:
                if enemy_board.grid[nr][nc] not in (Cell.HIT, Cell.MISS):
                    if (nr, nc) not in self.visited_target:
                        self.visited_target.add((nr, nc))
                        self.bfs_queue.append((nr, nc))

    def choose_target_bfs(self, enemy_board):
        """
        Uses BFS queue filled only from hits.
        If queue empties, fall back to HUNT.
        """
        while self.bfs_queue:
            r, c = self.bfs_queue.popleft()
            if enemy_board.grid[r][c] in (Cell.HIT, Cell.MISS):
                # already resolved; skip
                continue
            return r, c

        # nothing more to target → back to hunt
        self.mode = "HUNT"
        return self.choose_hunt_target(enemy_board)

    # ---------- PUBLIC API ---------- #

    def choose_shot(self, enemy_board):
        if self.mode == "HUNT":
            self.recompute_hunt_prob(enemy_board)
            return self.choose_hunt_target(enemy_board)
        else:
            return self.choose_target_bfs(enemy_board)

    def notify_result(self, r, c, result, enemy_board):
        if result == "HIT":
            # enter / stay in target mode and add neighbours only for THIS red cell
            self.mode = "TARGET"
            self._add_neighbours_of_hit(r, c, enemy_board)

        elif result == "SUNK":
            # Ship destroyed: clear targeting, go back to hunt, shrink ship list
            self.mode = "HUNT"
            self.bfs_queue.clear()
            self.visited_target.clear()
            if self.remaining_ship_lengths:
                # simple: assume smallest ship sunk last
                self.remaining_ship_lengths.pop()

        elif result == "MISS":
            # nothing special; queue already set up by HIT logic
            pass
