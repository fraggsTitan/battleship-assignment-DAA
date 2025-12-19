# ui_pygame.py
import sys
import pygame

from Controller import Controller
from Graph import Cell
from States import GameState

BOARD_SIZE = 10
CELL_SIZE = 40
MARGIN_TOP = 80
MARGIN_SIDE = 60
GAP_BETWEEN_BOARDS = 120

WINDOW_WIDTH = MARGIN_SIDE * 2 + BOARD_SIZE * CELL_SIZE * 2 + GAP_BETWEEN_BOARDS
WINDOW_HEIGHT = MARGIN_TOP + BOARD_SIZE * CELL_SIZE + 120

BG_COLOR = (15, 20, 30)
GRID_COLOR = (200, 200, 200)
TEXT_COLOR = (240, 240, 240)

COLOR_EMPTY = (40, 80, 120)
COLOR_SHIP = (70, 140, 70)
COLOR_HIT = (200, 60, 60)
COLOR_MISS = (150, 150, 160)
COLOR_HIGHLIGHT = (255, 255, 0)

pygame.init()
FONT = pygame.font.SysFont("consolas", 20)
BIG_FONT = pygame.font.SysFont("consolas", 28, bold=True)


def draw_board(surface, board, top_left, reveal_ships=False, title=""):
    x0, y0 = top_left

    if title:
        label = BIG_FONT.render(title, True, TEXT_COLOR)
        surface.blit(label, (x0, y0 - 40))

    # column labels
    for c in range(BOARD_SIZE):
        ch = chr(ord("A") + c)
        txt = FONT.render(ch, True, TEXT_COLOR)
        surface.blit(
            txt,
            (x0 + c * CELL_SIZE + CELL_SIZE // 2 - txt.get_width() // 2, y0 - 25),
        )

    # row labels
    for r in range(BOARD_SIZE):
        txt = FONT.render(str(r), True, TEXT_COLOR)
        surface.blit(
            txt,
            (x0 - 25, y0 + r * CELL_SIZE + CELL_SIZE // 2 - txt.get_height() // 2),
        )

    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            cell = board.grid[r][c]
            rect = pygame.Rect(
                x0 + c * CELL_SIZE, y0 + r * CELL_SIZE, CELL_SIZE, CELL_SIZE
            )

            if cell == Cell.EMPTY:
                color = COLOR_EMPTY
            elif cell == Cell.SHIP:
                color = COLOR_SHIP if reveal_ships else COLOR_EMPTY
            elif cell == Cell.HIT:
                color = COLOR_HIT
            elif cell == Cell.MISS:
                color = COLOR_MISS
            else:
                color = COLOR_EMPTY

            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, GRID_COLOR, rect, 1)


def coord_from_mouse(pos, board_top_left):
    x0, y0 = board_top_left
    mx, my = pos
    if mx < x0 or my < y0:
        return None
    dx = mx - x0
    dy = my - y0
    c = dx // CELL_SIZE
    r = dy // CELL_SIZE
    if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
        return r, c
    return None


def main():
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Battleship – DAA AI")

    clock = pygame.time.Clock()
    game = Controller()

    player_anchor = (MARGIN_SIDE, MARGIN_TOP)
    cpu_anchor = (MARGIN_SIDE + BOARD_SIZE * CELL_SIZE + GAP_BETWEEN_BOARDS, MARGIN_TOP)

    message = "Your turn: click on the RIGHT board to fire."

    running = True
    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif (
                event.type == pygame.MOUSEBUTTONDOWN
                and not game.is_over()
                and game.state == GameState.PLAYER_TURN
            ):
                pos = pygame.mouse.get_pos()
                target = coord_from_mouse(pos, cpu_anchor)
                if target is None:
                    continue
                r, c = target
                result = game.player_shot(r, c)
                col = chr(ord("A") + c)
                message = f"You fired at {col}{r}: {result}"

                if not game.is_over() and game.state == GameState.CPU_TURN:
                    pygame.time.delay(350)
                    cr, cc, cres = game.cpu_turn()
                    ccol = chr(ord("A") + cc)
                    message = f"CPU fired at {ccol}{cr}: {cres}"

        if game.is_over():
            if game.cpu_board.all_sunk():
                final = "YOU WIN!"
            elif game.player_board.all_sunk():
                final = "CPU WINS!"
            else:
                final = "Game over."
        else:
            final = ""

        screen.fill(BG_COLOR)
        draw_board(screen, game.player_board, player_anchor, True, "YOUR BOARD")
        draw_board(screen, game.cpu_board, cpu_anchor, False, "CPU BOARD")

        msg_surf = FONT.render(message, True, TEXT_COLOR)
        screen.blit(
            msg_surf,
            (MARGIN_SIDE, MARGIN_TOP + BOARD_SIZE * CELL_SIZE + 30),
        )

        if final:
            final_surf = BIG_FONT.render(final, True, COLOR_HIGHLIGHT)
            screen.blit(
                final_surf,
                (MARGIN_SIDE, MARGIN_TOP + BOARD_SIZE * CELL_SIZE + 60),
            )

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
