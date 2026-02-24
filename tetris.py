# tetris_game_phyton
import pygame
import random
import sys

CELL_SIZE = 30
COLS = 10
ROWS = 20
WIDTH = CELL_SIZE * COLS
HEIGHT = CELL_SIZE * ROWS
FPS = 60

SHAPES = [
    [[1,1,1,1]],
    [[1,1],[1,1]],
    [[0,1,0],[1,1,1]],
    [[1,0,0],[1,1,1]],
    [[0,0,1],[1,1,1]],
    [[1,1,0],[0,1,1]],
    [[0,1,1],[1,1,0]]
]

COLORS = [
    (0,255,255),
    (255,255,0),
    (128,0,128),
    (0,0,255),
    (255,165,0),
    (0,255,0),
    (255,0,0)
]

class Piece:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = COLORS[SHAPES.index(shape)]

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

def create_grid(locked):
    grid = [[(0,0,0) for _ in range(COLS)] for _ in range(ROWS)]
    for (x,y), color in locked.items():
        if y >= 0:
            grid[y][x] = color
    return grid

def valid_space(piece, grid):
    for y,row in enumerate(piece.shape):
        for x,cell in enumerate(row):
            if cell:
                new_x = x + piece.x
                new_y = y + piece.y
                if new_x < 0 or new_x >= COLS or new_y >= ROWS:
                    return False
                if new_y >= 0 and grid[new_y][new_x] != (0,0,0):
                    return False
    return True

def clear_rows(locked):
    rows_to_clear = []
    for y in range(ROWS):
        count = 0
        for x in range(COLS):
            if (x,y) in locked:
                count += 1
        if count == COLS:
            rows_to_clear.append(y)

    for y in rows_to_clear:
        for x in range(COLS):
            del locked[(x,y)]

    if rows_to_clear:
        for key in sorted(list(locked), key=lambda k: k[1])[::-1]:
            x, y = key
            shift = sum(1 for cleared_y in rows_to_clear if y < cleared_y)
            if shift > 0:
                locked[(x, y + shift)] = locked.pop((x,y))

def draw_grid(surface, grid):
    for y in range(ROWS):
        for x in range(COLS):
            pygame.draw.rect(surface, grid[y][x],
                             (x*CELL_SIZE, y*CELL_SIZE,
                              CELL_SIZE, CELL_SIZE))
    for x in range(COLS):
        pygame.draw.line(surface,(40,40,40),
                         (x*CELL_SIZE,0),
                         (x*CELL_SIZE,HEIGHT))
    for y in range(ROWS):
        pygame.draw.line(surface,(40,40,40),
                         (0,y*CELL_SIZE),
                         (WIDTH,y*CELL_SIZE))

def draw_game_over(screen):
    font = pygame.font.SysFont("Arial", 50)
    text = font.render("GAME OVER", True, (255,0,0))
    screen.blit(text, (WIDTH//2 - text.get_width()//2,
                       HEIGHT//2 - text.get_height()//2))
    pygame.display.update()
    pygame.time.delay(3000)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    locked = {}
    current = Piece(3,0,random.choice(SHAPES))

    fall_time = 0
    fall_speed = 0.5

    running = True
    while running:
        dt = clock.tick(FPS)/1000
        fall_time += dt

        grid = create_grid(locked)

        # --- Otomatik düşme ---
        if fall_time >= fall_speed:
            fall_time = 0
            current.y += 1
            if not valid_space(current, grid):
                current.y -= 1

                # Kilitle
                for y,row in enumerate(current.shape):
                    for x,cell in enumerate(row):
                        if cell:
                            locked[(x+current.x, y+current.y)] = current.color

                clear_rows(locked)

                # Yeni parça
                current = Piece(3,0,random.choice(SHAPES))

                # --- GAME OVER KONTROL ---
                if not valid_space(current, create_grid(locked)):
                    draw_game_over(screen)
                    running = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current.x -= 1
                    if not valid_space(current, grid):
                        current.x += 1

                if event.key == pygame.K_RIGHT:
                    current.x += 1
                    if not valid_space(current, grid):
                        current.x -= 1

                if event.key == pygame.K_UP:
                    old = current.shape
                    current.rotate()
                    if not valid_space(current, grid):
                        current.shape = old

                if event.key == pygame.K_DOWN:
                    current.y += 1
                    if not valid_space(current, grid):
                        current.y -= 1

        screen.fill((0,0,0))

        for y,row in enumerate(current.shape):
            for x,cell in enumerate(row):
                if cell:
                    grid[y+current.y][x+current.x] = current.color

        draw_grid(screen, grid)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
