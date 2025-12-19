import random
import string

BOARD_SIZE = 10
SHIP_SIZES = [5, 4, 3, 3, 2]

EMPTY = '.'
SHIP = 'S'
HIT = 'X'
MISS = 'O'


# ---------- Board utilities ----------

def create_board():
    return [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]


def print_board(board, show_ships=True):
    print("   " + " ".join(str(i) for i in range(BOARD_SIZE)))
    for r in range(BOARD_SIZE):
        row_label = string.ascii_uppercase[r]
        row_str = []
        for c in range(BOARD_SIZE):
            cell = board[r][c]
            if not show_ships and cell == SHIP:
                row_str.append(EMPTY)
            else:
                row_str.append(cell)
        print(f"{row_label}  " + " ".join(row_str))
    print()


def in_bounds(r, c):
    return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE


def can_place_ship(board, r, c, length, orientation):
    if orientation == 'H':
        if c + length > BOARD_SIZE:
            return False
        for i in range(length):
            if board[r][c + i] != EMPTY:
                return False
    else:
        if r + length > BOARD_SIZE:
            return False
        for i in range(length):
            if board[r + i][c] != EMPTY:
                return False
    return True


def place_ship(board, r, c, length, orientation):
    if orientation == 'H':
        for i in range(length):
            board[r][c + i] = SHIP
    else:
        for i in range(length):
            board[r + i][c] = SHIP


def random_place_ships(board, shipsizes):
    for length in shipsizes:
        placed = False
        while not placed:
            r = random.randint(0, BOARD_SIZE - 1)
            c = random.randint(0, BOARD_SIZE - 1)
            orientation = random.choice(['H', 'V'])
            if can_place_ship(board, r, c, length, orientation):
                place_ship(board, r, c, length, orientation)
                placed = True


def parse_coord(coord_str):
    coord_str = coord_str.strip().upper()
    if ' ' in coord_str:
        parts = coord_str.split()
        if len(parts) != 2:
            return None
        r_part, c_part = parts
        if len(r_part) == 1 and r_part.isalpha() and c_part.isdigit():
            r = ord(r_part) - ord('A')
            c = int(c_part)
            if in_bounds(r, c):
                return r, c
        if r_part.isdigit() and c_part.isdigit():
            r = int(r_part)
            c = int(c_part)
            if in_bounds(r, c):
                return r, c
        return None
    else:
        if len(coord_str) < 2:
            return None
        row_char = coord_str[0]
        col_part = coord_str[1:]
        if row_char.isalpha() and col_part.isdigit():
            r = ord(row_char) - ord('A')
            c = int(col_part)
            if in_bounds(r, c):
                return r, c
        return None


def all_ships_sunk(board):
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] == SHIP:
                return False
    return True


# ---------- Ship extraction & sunk detection ----------

def extract_ships(board):
    """Return list of ships; each ship is list of (r, c) cells."""
    visited = [[False] * BOARD_SIZE for _ in range(BOARD_SIZE)]
    ships = []
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] == SHIP and not visited[r][c]:
                stack = [(r, c)]
                visited[r][c] = True
                cells = []
                while stack:
                    cr, cc = stack.pop()
                    cells.append((cr, cc))
                    for nr, nc in [(cr - 1, cc), (cr + 1, cc), (cr, cc - 1), (cr, cc + 1)]:
                        if in_bounds(nr, nc) and not visited[nr][nc] and board[nr][nc] == SHIP:
                            visited[nr][nc] = True
                            stack.append((nr, nc))
                ships.append(cells)
    return ships


def remaining_ship_sizes(board, ships):
    sizes = []
    for ship in ships:
        if any(board[r][c] == SHIP or board[r][c] == HIT for (r, c) in ship):
            sizes.append(len(ship))
    sizes.sort(reverse=True)
    return sizes


def check_and_announce_sunk(board, ships, r, c, owner_name):
    """Check if the ship containing (r,c) is now fully HIT; if yes, print a message."""
    for ship in ships:
        if (r, c) in ship:
            if all(board[sr][sc] == HIT for (sr, sc) in ship):
                size = len(ship)
                print(f"{owner_name}'s ship of size {size} is destroyed!")
            break


# ---------- Player ship placement ----------

def player_place_ships(board):
    print("Place your ships on the 10x10 grid.")
    print("Rows: A-J, Columns: 0-9.")
    print("Example coordinate inputs: A0, A 0, 3 5")
    print_board(board, show_ships=True)

    for length in SHIP_SIZES:
        placed = False
        while not placed:
            print(f"Place ship of length {length}.")
            pos_str = input("Enter start coordinate (e.g., A0 or 3 5): ")
            coord = parse_coord(pos_str)
            if coord is None:
                print("Invalid coordinate. Try again.")
                continue
            r, c = coord
            orient = input("Orientation (H/V): ").strip().upper()
            if orient not in ['H', 'V']:
                print("Invalid orientation. Use H or V.")
                continue
            if not can_place_ship(board, r, c, length, orient):
                print("Cannot place ship there (out of bounds or overlap). Try again.")
                continue
            place_ship(board, r, c, length, orient)
            print_board(board, show_ships=True)
            placed = True

    input("All ships placed. Press Enter to continue...")


# ---------- AI state and logic (Hunt/Target + parity) ----------

class AIState:
    def __init__(self):
        self.mode = "HUNT"            # "HUNT" or "TARGET"
        self.target_stack = []        # candidate target cells
        self.tried = set()            # cells already fired at
        self.last_hits = []           # recent hit coordinates (for line extension)


def ai_parity_cells(tried, smallest_ship_len):
    """Generate all parity cells that match smallest ship length and are not tried."""
    candidates = []
    # Simple checkerboard parity based on smallest ship: (r + c) % smallest_ship_len == 0
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if (r, c) not in tried and (r + c) % smallest_ship_len == 0:
                candidates.append((r, c))
    random.shuffle(candidates)
    return candidates


def ai_get_shot(ai_state, ships_remaining_sizes):
    # If in TARGET mode, exhaust target_stack first
    while ai_state.mode == "TARGET" and ai_state.target_stack:
        r, c = ai_state.target_stack.pop()
        if (r, c) not in ai_state.tried and in_bounds(r, c):
            return r, c

    # No targets left, back to HUNT
    ai_state.mode = "HUNT"

    if ships_remaining_sizes:
        smallest_ship = min(ships_remaining_sizes)
    else:
        smallest_ship = 2

    parity_candidates = ai_parity_cells(ai_state.tried, smallest_ship)

    # Prefer parity cells
    for r, c in parity_candidates:
        return r, c

    # Fallback: any random untried cell
    while True:
        r = random.randint(0, BOARD_SIZE - 1)
        c = random.randint(0, BOARD_SIZE - 1)
        if (r, c) not in ai_state.tried:
            return r, c


def ai_add_targets(ai_state, r, c, player_board):
    """Add neighbors intelligently to target_stack, trying to extend lines."""
    ai_state.last_hits.append((r, c))

    # If multiple hits, try to determine orientation
    if len(ai_state.last_hits) >= 2:
        r1, c1 = ai_state.last_hits[-2]
        r2, c2 = ai_state.last_hits[-1]
        if r1 == r2:  # horizontal line
            for dc in [-1, 1]:
                nc = c2 + dc
                if in_bounds(r2, nc) and (r2, nc) not in ai_state.tried:
                    if player_board[r2][nc] in [EMPTY, SHIP]:
                        ai_state.target_stack.append((r2, nc))
            return
        elif c1 == c2:  # vertical line
            for dr in [-1, 1]:
                nr = r2 + dr
                if in_bounds(nr, c2) and (nr, c2) not in ai_state.tried:
                    if player_board[nr][c2] in [EMPTY, SHIP]:
                        ai_state.target_stack.append((nr, c2))
            return

    # Otherwise, add all four neighbors
    neighbors = [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]
    for nr, nc in neighbors:
        if in_bounds(nr, nc) and (nr, nc) not in ai_state.tried:
            if player_board[nr][nc] in [EMPTY, SHIP]:
                ai_state.target_stack.append((nr, nc))


def ai_clear_line_memory_if_ship_sunk(ai_state, player_board, player_ships):
    # If all recent hits belong to ships that are now fully sunk, clear last_hits
    remaining_hits = []
    for (r, c) in ai_state.last_hits:
        if player_board[r][c] == HIT:
            # still a hit; might be part of unsunk ship
            remaining_hits.append((r, c))
    ai_state.last_hits = remaining_hits
    if not ai_state.last_hits:
        ai_state.mode = "HUNT"


# ---------- Game loop ----------

def main():
    print("=== Battleship: Player vs PC (Hunt/Target + Parity AI) ===")
    print("Legend: '.' = unknown/water, 'S' = your ship, 'X' = hit, 'O' = miss")
    print()

    # Create boards
    player_board = create_board()
    ai_board = create_board()

    # Player places ships
    player_place_ships(player_board)

    # AI places ships randomly
    random_place_ships(ai_board, SHIP_SIZES)
    print("PC has placed its ships.")
    input("Press Enter to start the game...")

    # Extract ship structures for sunk detection
    player_ships = extract_ships(player_board)
    ai_ships = extract_ships(ai_board)

    # Tracking boards for shots
    player_tracking = create_board()  # what player sees of AI
    ai_tracking = create_board()      # what AI has done to player

    ai_state = AIState()
    current_player = "PLAYER"
    turn_number = 1

    while True:
        print(f"\n=== Turn {turn_number} ===")

        if current_player == "PLAYER":
            print("\nYour board:")
            print_board(player_board, show_ships=True)
            print("Enemy board (your view):")
            print_board(player_tracking, show_ships=False)
            print("Your remaining ships:", remaining_ship_sizes(player_board, player_ships))
            print("Enemy remaining ships:", remaining_ship_sizes(ai_board, ai_ships))

            coord_str = input("Your shot (e.g., A0 or 3 5): ")
            coord = parse_coord(coord_str)
            if coord is None:
                print("Invalid coordinate. Try again.")
                continue
            r, c = coord
            if player_tracking[r][c] in [HIT, MISS]:
                print("You already shot there. Try again.")
                continue

            if ai_board[r][c] == SHIP:
                print("You HIT a ship!")
                ai_board[r][c] = HIT
                player_tracking[r][c] = HIT
                check_and_announce_sunk(ai_board, ai_ships, r, c, "Enemy")
            elif ai_board[r][c] == EMPTY:
                print("You MISSED.")
                ai_board[r][c] = MISS
                player_tracking[r][c] = MISS
            else:
                print("That cell was already resolved. Try again.")
                continue

            if all_ships_sunk(ai_board):
                print("\nYou sank all enemy ships. You WIN!")
                break

            current_player = "AI"

        else:  # AI turn
            print("\nPC's turn...")

            ships_rem = remaining_ship_sizes(player_board, player_ships)
            r, c = ai_get_shot(ai_state, ships_rem)
            ai_state.tried.add((r, c))

            print(f"PC fires at {string.ascii_uppercase[r]}{c}")
            if player_board[r][c] == SHIP:
                print("PC HIT your ship!")
                player_board[r][c] = HIT
                ai_tracking[r][c] = HIT
                ai_state.mode = "TARGET"
                ai_add_targets(ai_state, r, c, player_board)
                check_and_announce_sunk(player_board, player_ships, r, c, "Your")
                ai_clear_line_memory_if_ship_sunk(ai_state, player_board, player_ships)
            elif player_board[r][c] == EMPTY:
                print("PC MISSED.")
                player_board[r][c] = MISS
                ai_tracking[r][c] = MISS
            else:
                print("PC repeated a cell, but this should not happen.")

            if all_ships_sunk(player_board):
                print("\nPC sank all your ships. You LOSE.")
                break

            current_player = "PLAYER"

        turn_number += 1

    print("\nGame over.")
    print("Your final board:")
    print_board(player_board, show_ships=True)
    print("Enemy final board:")
    print_board(ai_board, show_ships=True)


if __name__ == "__main__":
    main()
