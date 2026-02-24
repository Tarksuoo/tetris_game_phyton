# tetris_game_phyton
import pygame
import random

CELL_SIZE = 30
COLS = 10
ROWS = 20
WIDTH = CELL_SIZE * COLS
HEIGHT = CELL_SIZE * ROWS
FPS = 60

SHAPES = [
    [[1,1,1,1]],
    [[1,1],
     [1,1]],
    [[0,1,0],
     [1,1,1]],
    [[1,0,0],
     [1,1,1]],
    [[0,0,1],
     [1,1,1]],
    [[1,1,0],
     [0,1,1]],
    [[0,1,1],
     [1,1,0]]
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
        grid[y][x] = color
    return grid


def valid_space(piece, grid):
    for y,row in enumerate(piece.shape):
        for x,cell in enumerate(row):
            if cell:
                if (x+piece.x < 0 or
                    x+piece.x >= COLS or
                    y+piece.y >= ROWS or
                    grid[y+piece.y][x+piece.x] != (0,0,0)):
                    return False
    return True


def clear_rows(grid, locked):
    for y in range(ROWS-1, -1, -1):
        if (0,0,0) not in grid[y]:
            for x in range(COLS):
                del locked[(x,y)]
            for key in sorted(list(locked), key=lambda k: k[1])[::-1]:
                x,row = key
                if row < y:
                    locked[(x,row+1)] = locked.pop((x,row))


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


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    locked = {}
    current = Piece(3,0,random.choice(SHAPES))

    fall_time = 0
    fall_speed = 0.5  # otomatik düşme süresi (saniye)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000
        fall_time += dt

        grid = create_grid(locked)

        # 🔽 Otomatik düşme
        if fall_time >= fall_speed:
            fall_time = 0
            current.y += 1
            if not valid_space(current, grid):
                current.y -= 1
                for y,row in enumerate(current.shape):
                    for x,cell in enumerate(row):
                        if cell:
                            locked[(x+current.x, y+current.y)] = current.color
                clear_rows(grid, locked)
                current = Piece(3,0,random.choice(SHAPES))

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
                    old_shape = current.shape
                    current.rotate()
                    if not valid_space(current, grid):
                        current.shape = old_shape

                # 🔥 Soft Drop (sadece hızlandırır)
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


if __name__ == "__main__":
    main()
