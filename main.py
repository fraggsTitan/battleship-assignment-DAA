# main.py
from Controller import Controller
from Graph import Cell

LETTER_MAP = "ABCDEFGHIJ"


def print_board(board, reveal=False, title=""):
    if title:
        print(title)
    print("   " + " ".join(LETTER_MAP[:board.size]))
    for r in range(board.size):
        row = []
        for c in range(board.size):
            cell = board.grid[r][c]
            if cell == Cell.EMPTY:
                ch = "."
            elif cell == Cell.SHIP:
                ch = "S" if reveal else "."
            elif cell == Cell.HIT:
                ch = "X"
            elif cell == Cell.MISS:
                ch = "o"
            row.append(ch)
        print(f"{r:2d} " + " ".join(row))
    print()


def parse_coord(inp):
    inp = inp.strip().replace(",", " ").upper()
    parts = inp.split()
    if len(parts) == 1:
        if len(parts[0]) < 2:
            return None
        letter = parts[0][0]
        num = parts[0][1:]
    elif len(parts) == 2:
        if parts[0].isalpha():
            letter, num = parts[0], parts[1]
        else:
            num, letter = parts[0], parts[1]
    else:
        return None

    if letter not in LETTER_MAP:
        return None
    try:
        row = int(num)
    except ValueError:
        return None
    col = LETTER_MAP.index(letter)
    return row, col


def main():
    game = Controller()
    print("Battleship – 10x10, ships: 5,4,3,3,2")

    while not game.is_over():
        print_board(game.player_board, reveal=True, title="[ YOUR BOARD ]")
        print_board(game.cpu_board, reveal=False, title="[ CPU BOARD ]")

        if game.state.name == "PLAYER_TURN":
            raw = input("Your shot (e.g., B7): ")
            parsed = parse_coord(raw)
            if parsed is None:
                print("Bad format.")
                continue
            r, c = parsed
            if not (0 <= r < 10 and 0 <= c < 10):
                print("Out of bounds.")
                continue
            res = game.player_shot(r, c)
            print("You:", res)
        else:
            r, c, res = game.cpu_turn()
            print(f"CPU fired at {LETTER_MAP[c]}{r}: {res}")

    print("\n=== GAME OVER ===")
    print_board(game.player_board, reveal=True, title="[ FINAL – YOUR BOARD ]")
    print_board(game.cpu_board, reveal=True, title="[ FINAL – CPU BOARD ]")
    if game.cpu_board.all_sunk():
        print("You WIN!")
    else:
        print("CPU WINS!")


if __name__ == "__main__":
    main()
