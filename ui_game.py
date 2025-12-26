# ui_pygame.py
import sys
import pygame
from board import BOARD_SIZE, SHIP_SIZES, SHIP, EMPTY, HIT, MISS
from game import BattleshipGame

pygame.init()

CELL = 40
MARGIN_TOP = 80
MARGIN_SIDE = 40
GAP = 120

WIDTH = MARGIN_SIDE * 2 + BOARD_SIZE * CELL * 2 + GAP
HEIGHT = MARGIN_TOP + BOARD_SIZE * CELL + 160

BG = (20, 24, 35)
GRID = (200, 200, 200)
TEXT = (240, 240, 240)
SHIP_COLOR   = (72, 170, 95)    # Fresh green (clearly visible on dark bg)
HIT_COLOR    = (220, 50, 50)    # Strong crimson red
MISS_COLOR   = (120, 140, 170)  # Cool steel gray-blue
HOVER_COLOR  = (255, 215, 0)    # Gold (very visible)
VALID_COLOR  = (80, 220, 120)   # Bright mint green
INVALID_COLOR= (255, 90, 90)    # Light danger red


FONT = pygame.font.SysFont("consolas", 20)
BIG = pygame.font.SysFont("consolas", 26, bold=True)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Battleship – Player vs PC")


def mouse_to_cell(pos, top_left):
    x0, y0 = top_left
    mx, my = pos
    if mx < x0 or my < y0:
        return None
    dx, dy = mx - x0, my - y0
    c = dx // CELL
    r = dy // CELL
    if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
        return r, c
    return None


def draw_hover(surface, top_left):
    pos = pygame.mouse.get_pos()
    cell = mouse_to_cell(pos, top_left)
    if cell:
        r, c = cell
        rect = pygame.Rect(
            top_left[0] + c * CELL,
            top_left[1] + r * CELL,
            CELL,
            CELL,
        )
        pygame.draw.rect(surface, HOVER_COLOR, rect, 2)


def draw_board(surface, board, top_left, reveal_ships=False, title=""):
    x0, y0 = top_left

    if title:
        label = BIG.render(title, True, TEXT)
        surface.blit(label, (x0, y0 - 40))

    # column labels
    for c in range(BOARD_SIZE):
        col_txt = FONT.render(str(c), True, TEXT)
        surface.blit(col_txt, (x0 + c * CELL + CELL // 2 - col_txt.get_width() // 2, y0 - 25))

    # row labels
    for r in range(BOARD_SIZE):
        row_txt = FONT.render(chr(ord('A') + r), True, TEXT)
        surface.blit(row_txt, (x0 - 25, y0 + r * CELL + CELL // 2 - row_txt.get_height() // 2))

    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            rect = pygame.Rect(x0 + c * CELL, y0 + r * CELL, CELL, CELL)

            base_color = (25, 30, 45) if (r + c) % 2 == 0 else (30, 35, 55)
            cell = board.grid[r][c]

            if cell == HIT:
                color = HIT_COLOR
            elif cell == MISS:
                color = MISS_COLOR
            elif cell == SHIP and reveal_ships:
                color = SHIP_COLOR
            else:
                color = base_color

            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, GRID, rect, 1)


def render_message(text):
    if "HIT" in text:
        color = HIT_COLOR
    elif "MISS" in text:
        color = MISS_COLOR
    else:
        color = TEXT
    return FONT.render(text, True, color)


def main():
    clock = pygame.time.Clock()
    game = BattleshipGame()

    player_anchor = (MARGIN_SIDE, MARGIN_TOP)
    ai_anchor = (MARGIN_SIDE + BOARD_SIZE * CELL + GAP, MARGIN_TOP)

    ships_to_place = SHIP_SIZES.copy()
    current_length = ships_to_place[0]
    orientation = 'H'
    placing_phase = True

    size_buttons = []
    bx = MARGIN_SIDE
    by = HEIGHT - 70
    for size in SHIP_SIZES:
        rect = pygame.Rect(bx, by, 50, 30)
        size_buttons.append((size, rect))
        bx += 60

    message = "Place your ships: select size, press R to rotate, click grid."

    running = True
    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    orientation = 'V' if orientation == 'H' else 'H'

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()

                if placing_phase:
                    for size, rect in size_buttons:
                        if rect.collidepoint(mx, my) and size in ships_to_place:
                            current_length = size

                    cell = mouse_to_cell((mx, my), player_anchor)
                    if cell:
                        r, c = cell
                        if game.player_can_place(r, c, current_length, orientation):
                            game.player_place(r, c, current_length, orientation)
                            ships_to_place.remove(current_length)
                            if ships_to_place:
                                current_length = ships_to_place[0]
                            else:
                                placing_phase = False
                                message = "Game start: fire on the RIGHT board."
                else:
                    if not (game.player_won() or game.ai_won()):
                        cell = mouse_to_cell((mx, my), ai_anchor)
                        if cell:
                            r, c = cell
                            res = game.player_shoot(r, c)
                            if res in ("HIT", "MISS"):
                                ar, ac, ares = game.ai_shoot()
                                if game.player_won():
                                    message = "YOU WIN! All enemy ships sunk."
                                elif game.ai_won():
                                    message = "PC WINS! Your fleet is destroyed."
                                else:
                                    message = f"You: {res} at {chr(ord('A')+r)}{c}, PC: {ares} at {chr(ord('A')+ar)}{ac}"
                            elif res == "REPEAT":
                                message = "You already shot there."

        screen.fill(BG)

        banner = BIG.render(
            "SHIP PLACEMENT" if placing_phase else "YOUR TURN",
            True,
            (180, 220, 180),
        )
        screen.blit(banner, (WIDTH // 2 - banner.get_width() // 2, 20))

        draw_board(
            screen,
            game.player_board,
            player_anchor,
            reveal_ships=True,
            title="YOUR BOARD",
        )

        draw_board(
            screen,
            game.player_view if not placing_phase else game.ai_board,
            ai_anchor,
            reveal_ships=False,
            title="PC BOARD",
        )

        if not placing_phase:
            draw_hover(screen, ai_anchor)

        if placing_phase:
            pos = pygame.mouse.get_pos()
            cell = mouse_to_cell(pos, player_anchor)
            if cell:
                r, c = cell
                valid = game.player_can_place(r, c, current_length, orientation)
                outline = VALID_COLOR if valid else INVALID_COLOR

                for i in range(current_length):
                    rr = r + (i if orientation == 'V' else 0)
                    cc = c + (i if orientation == 'H' else 0)
                    if 0 <= rr < BOARD_SIZE and 0 <= cc < BOARD_SIZE:
                        rect = pygame.Rect(
                            player_anchor[0] + cc * CELL,
                            player_anchor[1] + rr * CELL,
                            CELL,
                            CELL,
                        )
                        pygame.draw.rect(screen, outline, rect, 2)

        for size, rect in size_buttons:
            color = (80, 120, 200) if size in ships_to_place else (60, 60, 60)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (0, 0, 0), rect, 1)
            label = FONT.render(str(size), True, TEXT)
            screen.blit(
                label,
                (rect.x + rect.width // 2 - label.get_width() // 2,
                 rect.y + rect.height // 2 - label.get_height() // 2),
            )

        orient_txt = FONT.render(f"Orientation: {orientation} (R to rotate)", True, TEXT)
        screen.blit(orient_txt, (MARGIN_SIDE, HEIGHT - 110))

        msg_surface = render_message(message)
        screen.blit(msg_surface, (MARGIN_SIDE, HEIGHT - 135))

        if not placing_phase and mouse_to_cell(pygame.mouse.get_pos(), ai_anchor):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
