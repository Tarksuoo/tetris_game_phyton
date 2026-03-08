# tetris_game_phyton
import pygame
import random
import sys

# --- Constants ---
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 620
BOARD_X = 100
BOARD_Y = 60
CELL = 28
COLS = 10
ROWS = 20

# Colors
BG       = (15, 15, 25)
GRID_COL = (30, 30, 45)
BORDER   = (60, 60, 90)
WHITE    = (230, 230, 240)
GRAY     = (120, 120, 140)
BLACK    = (0, 0, 0)

COLORS = [
    None,
    (0,   210, 210),  # I - cyan
    (220, 180,  20),  # O - yellow
    (160,  40, 200),  # T - purple
    ( 40, 160,  40),  # S - green
    (210,  40,  40),  # Z - red
    ( 40,  80, 220),  # J - blue
    (220, 130,  20),  # L - orange
]

SHAPES = [
    None,
    [[1,1,1,1]],                          # I
    [[2,2],[2,2]],                        # O
    [[0,3,0],[3,3,3]],                    # T
    [[0,4,4],[4,4,0]],                    # S
    [[5,5,0],[0,5,5]],                    # Z
    [[6,0,0],[6,6,6]],                    # J
    [[0,0,7],[7,7,7]],                    # L
]

# --- Helper functions ---
def rotate(shape):
    return [list(row) for row in zip(*shape[::-1])]

def new_piece():
    idx = random.randint(1, 7)
    return {"shape": [row[:] for row in SHAPES[idx]], "x": 3, "y": 0, "id": idx}

def valid(board, piece, ox=0, oy=0, shape=None):
    s = shape if shape else piece["shape"]
    for r, row in enumerate(s):
        for c, val in enumerate(row):
            if val:
                nx, ny = piece["x"] + c + ox, piece["y"] + r + oy
                if nx < 0 or nx >= COLS or ny >= ROWS:
                    return False
                if ny >= 0 and board[ny][nx]:
                    return False
    return True

def place(board, piece):
    for r, row in enumerate(piece["shape"]):
        for c, val in enumerate(row):
            if val:
                board[piece["y"] + r][piece["x"] + c] = val

def clear_lines(board):
    full = [i for i, row in enumerate(board) if all(row)]
    for i in full:
        board.pop(i)
        board.insert(0, [0]*COLS)
    return len(full)

def ghost(board, piece):
    g = {"shape": piece["shape"], "x": piece["x"], "y": piece["y"], "id": piece["id"]}
    while valid(board, g, oy=1):
        g["y"] += 1
    return g

def draw_cell(surf, x, y, color, alpha=255):
    rect = pygame.Rect(BOARD_X + x*CELL, BOARD_Y + y*CELL, CELL-1, CELL-1)
    if alpha < 255:
        s = pygame.Surface((CELL-1, CELL-1), pygame.SRCALPHA)
        s.fill((*color, alpha))
        surf.blit(s, rect.topleft)
    else:
        pygame.draw.rect(surf, color, rect, border_radius=3)
        highlight = pygame.Rect(rect.x+2, rect.y+2, rect.w-4, 5)
        light = tuple(min(255, c+60) for c in color)
        pygame.draw.rect(surf, light, highlight, border_radius=2)

def draw_mini(surf, shape, cx, cy, color):
    off_x = cx - len(shape[0])*10//2
    off_y = cy - len(shape)*10//2
    for r, row in enumerate(shape):
        for c, val in enumerate(row):
            if val:
                pygame.draw.rect(surf, color,
                    (off_x + c*10, off_y + r*10, 9, 9), border_radius=2)

# --- Main ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()

    font_big   = pygame.font.SysFont("consolas", 32, bold=True)
    font_med   = pygame.font.SysFont("consolas", 18, bold=True)
    font_small = pygame.font.SysFont("consolas", 13)

    def reset():
        return {
            "board":  [[0]*COLS for _ in range(ROWS)],
            "piece":  new_piece(),
            "next":   new_piece(),
            "score":  0,
            "lines":  0,
            "level":  1,
            "over":   False,
            "paused": False,
            "fall_t": 0,
            "lock_t": 0,
            "locking": False,
        }

    state = reset()
    SCORE_TABLE = {1: 100, 2: 300, 3: 500, 4: 800}

    while True:
        dt = clock.tick(60)
        s = state

        # --- Events ---
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_q or ev.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

                if s["over"]:
                    if ev.key == pygame.K_r:
                        state = reset(); s = state
                    continue

                if ev.key == pygame.K_p:
                    s["paused"] = not s["paused"]

                if s["paused"]:
                    continue

                if ev.key == pygame.K_LEFT:
                    if valid(s["board"], s["piece"], ox=-1):
                        s["piece"]["x"] -= 1
                        s["locking"] = False

                if ev.key == pygame.K_RIGHT:
                    if valid(s["board"], s["piece"], ox=1):
                        s["piece"]["x"] += 1
                        s["locking"] = False

                if ev.key == pygame.K_UP:
                    rot = rotate(s["piece"]["shape"])
                    if valid(s["board"], s["piece"], shape=rot):
                        s["piece"]["shape"] = rot
                        s["locking"] = False

                if ev.key == pygame.K_DOWN:
                    if valid(s["board"], s["piece"], oy=1):
                        s["piece"]["y"] += 1
                        s["score"] += 1
                        s["fall_t"] = 0

                if ev.key == pygame.K_SPACE:
                    g = ghost(s["board"], s["piece"])
                    drop = g["y"] - s["piece"]["y"]
                    s["piece"]["y"] = g["y"]
                    s["score"] += drop * 2
                    place(s["board"], s["piece"])
                    cleared = clear_lines(s["board"])
                    s["lines"] += cleared
                    s["score"] += SCORE_TABLE.get(cleared, 0) * s["level"]
                    s["level"] = s["lines"] // 10 + 1
                    s["piece"] = s["next"]
                    s["next"]  = new_piece()
                    s["locking"] = False
                    if not valid(s["board"], s["piece"]):
                        s["over"] = True

        if s["over"] or s["paused"]:
            pass
        else:
            speed = max(100, 800 - (s["level"]-1)*70)
            s["fall_t"] += dt
            if s["fall_t"] >= speed:
                s["fall_t"] = 0
                if valid(s["board"], s["piece"], oy=1):
                    s["piece"]["y"] += 1
                    s["locking"] = False
                else:
                    s["locking"] = True

            if s["locking"]:
                s["lock_t"] += dt
                if s["lock_t"] >= 500:
                    s["lock_t"] = 0
                    s["locking"] = False
                    place(s["board"], s["piece"])
                    cleared = clear_lines(s["board"])
                    s["lines"] += cleared
                    s["score"] += SCORE_TABLE.get(cleared, 0) * s["level"]
                    s["level"] = s["lines"] // 10 + 1
                    s["piece"] = s["next"]
                    s["next"]  = new_piece()
                    if not valid(s["board"], s["piece"]):
                        s["over"] = True

        # --- Draw ---
        screen.fill(BG)

        # Board background
        pygame.draw.rect(screen, (20, 20, 35),
            (BOARD_X-2, BOARD_Y-2, COLS*CELL+4, ROWS*CELL+4), border_radius=4)

        # Grid lines
        for r in range(ROWS+1):
            pygame.draw.line(screen, GRID_COL,
                (BOARD_X, BOARD_Y+r*CELL), (BOARD_X+COLS*CELL, BOARD_Y+r*CELL))
        for c in range(COLS+1):
            pygame.draw.line(screen, GRID_COL,
                (BOARD_X+c*CELL, BOARD_Y), (BOARD_X+c*CELL, BOARD_Y+ROWS*CELL))

        # Board pieces
        for r in range(ROWS):
            for c in range(COLS):
                if s["board"][r][c]:
                    draw_cell(screen, c, r, COLORS[s["board"][r][c]])

        if not s["over"]:
            # Ghost
            g = ghost(s["board"], s["piece"])
            for r, row in enumerate(g["shape"]):
                for c, val in enumerate(row):
                    if val and g["y"]+r != s["piece"]["y"]+r:
                        draw_cell(screen, g["x"]+c, g["y"]+r, COLORS[val], alpha=55)

            # Active piece
            for r, row in enumerate(s["piece"]["shape"]):
                for c, val in enumerate(row):
                    if val and s["piece"]["y"]+r >= 0:
                        draw_cell(screen, s["piece"]["x"]+c, s["piece"]["y"]+r, COLORS[val])

        # Board border
        pygame.draw.rect(screen, BORDER,
            (BOARD_X-2, BOARD_Y-2, COLS*CELL+4, ROWS*CELL+4), 2, border_radius=4)

        # --- Side panel ---
        px = BOARD_X + COLS*CELL + 20

        # NEXT
        screen.blit(font_med.render("NEXT", True, GRAY), (px, BOARD_Y))
        next_box = pygame.Rect(px, BOARD_Y+22, 80, 60)
        pygame.draw.rect(screen, (20, 20, 35), next_box, border_radius=4)
        pygame.draw.rect(screen, BORDER, next_box, 2, border_radius=4)
        nid = s["next"]["id"]
        draw_mini(screen, s["next"]["shape"],
                  next_box.centerx, next_box.centery, COLORS[nid])

        # SCORE
        screen.blit(font_med.render("SCORE", True, GRAY),  (px, BOARD_Y+100))
        screen.blit(font_big.render(str(s["score"]), True, WHITE), (px, BOARD_Y+118))

        screen.blit(font_med.render("LINES", True, GRAY),  (px, BOARD_Y+175))
        screen.blit(font_big.render(str(s["lines"]), True, WHITE), (px, BOARD_Y+193))

        screen.blit(font_med.render("LEVEL", True, GRAY),  (px, BOARD_Y+250))
        screen.blit(font_big.render(str(s["level"]), True, WHITE), (px, BOARD_Y+268))

        # Controls hint
        hints = ["← → Move", "↑  Rotate", "↓  Soft drop",
                 "SPC Hard drop", "P  Pause", "Q  Quit"]
        for i, h in enumerate(hints):
            screen.blit(font_small.render(h, True, (70,70,95)),
                        (px, BOARD_Y + 330 + i*18))

        # Overlays
        if s["paused"]:
            ov = pygame.Surface((COLS*CELL, ROWS*CELL), pygame.SRCALPHA)
            ov.fill((0,0,0,160))
            screen.blit(ov, (BOARD_X, BOARD_Y))
            t = font_big.render("PAUSED", True, WHITE)
            screen.blit(t, (BOARD_X + COLS*CELL//2 - t.get_width()//2,
                            BOARD_Y + ROWS*CELL//2 - 20))
            t2 = font_small.render("press P to continue", True, GRAY)
            screen.blit(t2, (BOARD_X + COLS*CELL//2 - t2.get_width()//2,
                             BOARD_Y + ROWS*CELL//2 + 20))

        if s["over"]:
            ov = pygame.Surface((COLS*CELL, ROWS*CELL), pygame.SRCALPHA)
            ov.fill((0,0,0,180))
            screen.blit(ov, (BOARD_X, BOARD_Y))
            t = font_big.render("GAME OVER", True, (220,60,60))
            screen.blit(t, (BOARD_X + COLS*CELL//2 - t.get_width()//2,
                            BOARD_Y + ROWS*CELL//2 - 30))
            t2 = font_med.render(f"Score: {s['score']}", True, WHITE)
            screen.blit(t2, (BOARD_X + COLS*CELL//2 - t2.get_width()//2,
                             BOARD_Y + ROWS*CELL//2 + 10))
            t3 = font_small.render("press R to restart", True, GRAY)
            screen.blit(t3, (BOARD_X + COLS*CELL//2 - t3.get_width()//2,
                             BOARD_Y + ROWS*CELL//2 + 40))

        # Title
        title = font_med.render("TETRIS", True, (80, 120, 220))
        screen.blit(title, (BOARD_X + COLS*CELL//2 - title.get_width()//2, 18))

        pygame.display.flip()

if __name__ == "__main__":
    main()
