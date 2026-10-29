"""
Conway's Game of Life
----------------------
Run directly in VSCode (F5 or `python game_of_life.py`).
No external dependencies — pure console animation.
"""

import os
import random
import time
import copy

ROWS = 20
COLS = 40
ALIVE_PROB = 0.2      # ~20% of cells start alive
GENERATIONS = 200
DELAY = 0.15           # seconds between frames
WRAPAROUND = True      # toroidal grid vs hard edges


def make_grid(rows, cols):
    return [[0 for _ in range(cols)] for _ in range(rows)]


def randomize(grid):
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            grid[r][c] = 1 if random.random() < ALIVE_PROB else 0


def count_neighbors(grid, r, c):
    rows, cols = len(grid), len(grid[0])
    count = 0
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            nr, nc = r + dr, c + dc
            if WRAPAROUND:
                nr %= rows
                nc %= cols
                count += grid[nr][nc]
            else:
                if 0 <= nr < rows and 0 <= nc < cols:
                    count += grid[nr][nc]
    return count


def step(grid):
    """Compute next generation into a fresh buffer — never mutate in place."""
    rows, cols = len(grid), len(grid[0])
    next_grid = make_grid(rows, cols)
    for r in range(rows):
        for c in range(cols):
            n = count_neighbors(grid, r, c)
            if grid[r][c] == 1:
                next_grid[r][c] = 1 if n in (2, 3) else 0
            else:
                next_grid[r][c] = 1 if n == 3 else 0
    return next_grid


def print_grid(grid, generation):
    os.system("cls" if os.name == "nt" else "clear")
    print(f"Generation {generation}")
    for row in grid:
        print("".join("#" if cell else "." for cell in row))


def load_glider(grid, top=0, left=0):
    """Seed a glider pattern at the given offset — moves 1 cell diagonally every 4 gens."""
    pattern = [
        (0, 1),
        (1, 2),
        (2, 0), (2, 1), (2, 2),
    ]
    for dr, dc in pattern:
        grid[top + dr][left + dc] = 1


def load_blinker(grid, top=0, left=0):
    """Seed a blinker — oscillates with period 2. Good sanity check."""
    for dc in range(3):
        grid[top][left + dc] = 1


def main():
    grid = make_grid(ROWS, COLS)

    # Comment/uncomment to try different seeds:
    randomize(grid)
    # load_glider(grid, top=1, left=1)
    # load_blinker(grid, top=5, left=5)

    for gen in range(GENERATIONS):
        print_grid(grid, gen)
        grid = step(grid)
        time.sleep(DELAY)


if __name__ == "__main__":
    main()