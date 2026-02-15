import random
from board import BOARD_SIZE, EMPTY, HIT, MISS
from graph import Vertex, GridGraph


class AIState:
    def __init__(self):
        self.mode = "HUNT"
        self.tried = set()
        self.target_hits = []
        self.target_dir = None   # 'H', 'V', or None


class BattleshipAI:
    def __init__(self):
        self.state = AIState()
        self.remaining_ships = [5, 4, 3, 3, 2]
        self.ship_size=5#for hunt mode

    # -------------------------------------------------
    # GRAPH TRAVERSAL (DFS on HIT components)
    # -------------------------------------------------
    def _hit_components(self, ai_view):
        graph = GridGraph(ai_view)
        visited = set()
        components = []

        for r in range(ai_view.size):
            for c in range(ai_view.size):
                if ai_view.grid[r][c] != HIT:
                    continue

                start = Vertex(r, c)
                if start in visited:
                    continue

                stack = [start]
                visited.add(start)
                comp = []

                # ---- DFS ----
                while stack:
                    v = stack.pop()
                    comp.append(v)

                    for n in graph.neighbors(v):
                        if n not in visited and ai_view.grid[n.r][n.c] == HIT:
                            visited.add(n)
                            stack.append(n)

                components.append(comp)

        return components

    # -------------------------------------------------
    # TARGET MODE (GREEDY EXPANSION)
    # -------------------------------------------------
    def _target_shot(self, ai_view):
        components = self._hit_components(ai_view)

        # If we already have target hits, lock to that component
        if self.state.target_hits:
            hit_set = set((v.r, v.c) for v in self.state.target_hits)
            for comp in components:
                if any((v.r, v.c) in hit_set for v in comp):
                    self.state.target_hits = comp
                    break
            else:
                comp = self.state.target_hits
        else:
            if not components:
                return None
            # First hit of a new ship
            comp = max(components, key=len)
            self.state.target_hits = comp



        # -------------------------------------------------
        # DISCOVERY PHASE (single hit)
        # -------------------------------------------------
        if len(comp) == 1:
            v = comp[0]

            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                nr, nc = v.r + dr, v.c + dc
                if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                    if (nr, nc) not in self.state.tried and ai_view.grid[nr][nc] == EMPTY:
                        return nr, nc

            return None

        # -------------------------------------------------
        # COMMIT PHASE (determine orientation once)
        # -------------------------------------------------
        rows = {v.r for v in comp}
        cols = {v.c for v in comp}

        if self.state.target_dir is None:
            if len(rows) == 1:
                self.state.target_dir = 'H'
            elif len(cols) == 1:
                self.state.target_dir = 'V'
            else:
                return None  # shouldn't happen

        # -------------------------------------------------
        # EXTENSION PHASE (guaranteed finish)
        # -------------------------------------------------
        if self.state.target_dir == 'H':
            r = next(iter(rows))
            cols = merge_sort(list(cols))  # Replace sorted(cols)

            for c in (cols[0] - 1, cols[-1] + 1):
                if 0 <= c < BOARD_SIZE:
                    if (r, c) not in self.state.tried and ai_view.grid[r][c] == EMPTY:
                        return r, c

        elif self.state.target_dir == 'V':
            c = next(iter(cols))
            rows = merge_sort(list(rows))  # Replace sorted(rows)

            for r in (rows[0] - 1, rows[-1] + 1):
                if 0 <= r < BOARD_SIZE:
                    if (r, c) not in self.state.tried and ai_view.grid[r][c] == EMPTY:
                        return r, c

        # -------------------------------------------------
        # RELEASE (ship is boxed in → sunk)
        # -------------------------------------------------
        blocked = True

        if self.state.target_dir == 'H':
            r = next(iter(rows))
            for c in (cols[0] - 1, cols[-1] + 1):
                if 0 <= c < BOARD_SIZE and ai_view.grid[r][c] == EMPTY:
                    blocked = False

        elif self.state.target_dir == 'V':
            c = next(iter(cols))
            for r in (rows[0] - 1, rows[-1] + 1):
                if 0 <= r < BOARD_SIZE and ai_view.grid[r][c] == EMPTY:
                    blocked = False

        if blocked:
            self.state.target_hits = []
            self.state.target_dir = None
            self.state.mode = "HUNT"

        return None




    # -------------------------------------------------
    # HUNT MODE (GREEDY PROBABILITY SCAN)
    # -------------------------------------------------
    def _hunt_shot(self, ai_view):
        while self.ship_size >= 2:
            scores = self._score_with_ship(ai_view, self.ship_size)

            # check if this ship size is still possible
            max_score = 0
            for _, _, s in scores:
                if s > max_score:
                    max_score = s

            if max_score > 0:
                return self._bucket_best_cell(scores)

            # ship cannot fit anywhere → permanently discard
            self.ship_size -= 1

        return None


    def _score_with_ship(self, ai_view, ship_len):
        score_grid = [[0]*BOARD_SIZE for _ in range(BOARD_SIZE)]
        scores = []

        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if (r, c) in self.state.tried:
                    continue

                if ai_view.grid[r][c] != EMPTY:
                    continue

                # ---- vertical ----
                can_fit = True
                for i in range(ship_len):
                    if r+i >= BOARD_SIZE or ai_view.grid[r+i][c] == MISS:
                        can_fit = False
                        break
                if can_fit:
                    for i in range(ship_len):
                        score_grid[r+i][c] += 1

                # ---- horizontal ----
                can_fit = True
                for i in range(ship_len):
                    if c+i >= BOARD_SIZE or ai_view.grid[r][c+i] == MISS:
                        can_fit = False
                        break
                if can_fit:
                    for i in range(ship_len):
                        score_grid[r][c+i] += 1

                scores.append((r, c, score_grid[r][c]))

        return scores


        
    #bucket sorting algorithm
    def _bucket_best_cell(self, scores):
        """
        Custom bucket sort:
        scores = [(r, c, score), ...]
        Returns (r, c) with highest score
        """

        # Find max score
        max_score = 0
        for _, _, s in scores:
            if s > max_score:
                max_score = s

        # Create buckets
        buckets = [[] for _ in range(max_score + 1)]

        # Fill buckets
        for r, c, s in scores:
            buckets[s].append((r, c))

        # Greedy: highest score first
        for score in range(max_score, -1, -1):
            if buckets[score]:
                return random.choice(buckets[score])

        return None


    # -------------------------------------------------
    # PUBLIC API
    # -------------------------------------------------
    def get_shot(self, ai_view):
        if self.state.mode == "TARGET":
            shot = self._target_shot(ai_view)
            if shot:
                return shot
            # TARGET persists, but we still must shoot
            # fallback to hunt for THIS turn only

        shot = self._hunt_shot(ai_view)
        if shot:
            return shot

        # ultimate fallback (never None)
        while True:
            r = random.randint(0, BOARD_SIZE - 1)
            c = random.randint(0, BOARD_SIZE - 1)
            if (r, c) not in self.state.tried:
                return r, c


    def update_after_shot(self, r, c, result, ai_view):
        self.state.tried.add((r, c))

        if result == "HIT":
            if self.state.mode != "TARGET":
                self.state.target_dir = None
            self.state.mode = "TARGET"
            self.state.target_hits.append(Vertex(r, c))

        elif result == "MISS":
            pass
        print("MODE:", self.state.mode)
        print("TARGET HITS:", self.state.target_hits)
        print("DIR:", self.state.target_dir)


# Custom merge sort implementation
def merge_sort(arr):
    if len(arr) > 1:
        mid = len(arr) // 2
        left_half = arr[:mid]
        right_half = arr[mid:]

        merge_sort(left_half)
        merge_sort(right_half)

        i = j = k = 0

        # Merge the sorted halves
        while i < len(left_half) and j < len(right_half):
            if left_half[i] < right_half[j]:
                arr[k] = left_half[i]
                i += 1
            else:
                arr[k] = right_half[j]
                j += 1
            k += 1

        # Copy remaining elements of left_half, if any
        while i < len(left_half):
            arr[k] = left_half[i]
            i += 1
            k += 1

        # Copy remaining elements of right_half, if any
        while j < len(right_half):
            arr[k] = right_half[j]
            j += 1
            k += 1

    return arr


