#!/usr/bin/env python3
"""My take on the 2048 game."""
import curses
import random
from dataclasses import dataclass
from enum import Enum, auto
from typing import Union

MATRIX_HEIGHT = 4
MATRIX_WIDTH = 4
CELL_WIDTH = 6
SCORE_WIDTH = 6


class Direction(Enum):
    """Game moves."""

    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()


@dataclass
class Cell:
    """Matrix's cell."""

    value: int = 0
    added: bool = False
    moved: bool = False
    new: bool = False

    def __str__(self) -> str:
        """Sting representation."""
        return str(self.value)

    def __eq__(self, other: object) -> bool:
        """Compare cell's value with another cell's value or an integer."""
        if not isinstance(other, (int, Cell)):
            return NotImplemented
        return self.value == (other if isinstance(other, int) else other.value)

    def __add__(self, other: Union[int, "Cell"]) -> None:
        """Add another cell's value or an integer."""
        add_value = other if isinstance(other, int) else other.value
        if self.value != 0 and add_value != 0:
            self.added = True
        self.moved = True
        self.value += add_value

    def __iadd__(self, other: Union[int, "Cell"]) -> "Cell":
        """Inplace add."""
        self + other
        return self

    def __bool__(self) -> bool:
        """Boolean operation."""
        return not self.value == 0


class Matrix:
    """Game matrix."""

    def __init__(self) -> None:
        """Initialize game matrix."""
        random.seed()

        self.matrix = [
            [Cell() for _ in range(MATRIX_WIDTH)] for _ in range(MATRIX_HEIGHT)
        ]
        self.add_new_value()
        self.add_new_value()
        self.score = 0

    def add_new_value(self) -> None:
        """
        Add a new value, chosen between 2 and 4, to a random free cell if available.

        2 has an 90% chances to be drawn.
        """
        free_cells = self.find_value(0)
        if not free_cells:
            return
        x, y = random.choice(free_cells)
        self.matrix[y][x].value = random.choices((2, 4), (90, 10))[0]
        self.matrix[y][x].new = True

    def is_full(self) -> bool:
        """Check if the matrix has empty (zero) cells or if cells can move."""
        if self.find_value(0):
            return False
        for y in range(0, MATRIX_HEIGHT):
            for x in range(0, MATRIX_WIDTH):
                if self.matrix[y][x] == 0:
                    continue
                if self.matrix[y][x].value in self.get_neighbors(x, y):
                    return False
        return True

    def find_value(self, value: int) -> list[tuple[int, int]]:
        """Get the cells' coordinates of a given value."""
        coordinates = []
        for y, row in enumerate(self.matrix):
            for x, cell in enumerate(row):
                if cell == value:
                    coordinates.append((x, y))
        return coordinates

    def get_neighbors(self, x: int, y: int) -> tuple[int, ...]:
        """Get values of the target cell's neighbors(N, S, E, W)."""
        neighbors = [0, 0, 0, 0]
        if y > 0:
            neighbors[0] = self.matrix[y - 1][x].value
        if y < MATRIX_HEIGHT - 1:
            neighbors[1] = self.matrix[y + 1][x].value
        if x < MATRIX_WIDTH - 1:
            neighbors[2] = self.matrix[y][x + 1].value
        if x > 0:
            neighbors[3] = self.matrix[y][x - 1].value
        return tuple(neighbors)

    def rotate_cw(self) -> None:
        """Rotate the matrix 90° clockwise."""
        rotated = list(zip(*reversed(self.matrix)))
        self.matrix = [list(element) for element in rotated]

    def rotate_ccw(self) -> None:
        """Rotate the matrix 90° counter clockwise."""
        rotated = list(zip(*reversed(self.matrix)))
        self.matrix = [list(element)[::-1] for element in rotated][::-1]

    def move(self, direction: Direction) -> None:
        r"""
        Move cells in the given direction.

        According to next method I can only move cells to the right so to move in other
        directions I rotate the matrix. ¯\_(ツ)_/¯
        """
        self.prepare_cells_to_move()
        if direction == Direction.UP:
            self.rotate_cw()
        if direction == Direction.DOWN:
            self.rotate_ccw()
        if direction == Direction.LEFT:
            self.rotate_cw()
            self.rotate_cw()

        for y in range(0, MATRIX_HEIGHT):
            for x in reversed(range(0, MATRIX_WIDTH)):
                if self.matrix[y][x] == 0 or x >= MATRIX_WIDTH - 1:
                    continue
                self.move_cell_to_right(x, y)
        if direction == Direction.UP:
            self.rotate_ccw()
        if direction == Direction.DOWN:
            self.rotate_cw()
        if direction == Direction.LEFT:
            self.rotate_ccw()
            self.rotate_ccw()
        if self.has_moved():
            self.add_new_value()

    def move_cell_to_right(self, x: int, y: int) -> None:
        """
        Move cells to the right.

        A non-zero cell moves freely over zero cells.
        If a cell of the same value is encountered, the cells are merged(values are
        added).
        If a different value is encountered, the movement stops.
        If a cell has already been merged it cannot be merged again during this turn.
        The rightmost cells are added first.
        """
        if self.matrix[y][x + 1] == 0 or (
            not self.matrix[y][x].added
            and not self.matrix[y][x + 1].added
            and self.matrix[y][x + 1] == self.matrix[y][x]
        ):
            self.matrix[y][x + 1] += self.matrix[y][x]
            if self.matrix[y][x + 1].added:
                self.score += self.matrix[y][x + 1].value
            self.matrix[y][x] = Cell()
            if x + 1 >= MATRIX_WIDTH - 1:
                return
            self.move_cell_to_right(x + 1, y)

    def has_moved(self) -> bool:
        """Check if cells have moved in the martix."""
        return any(cell.moved for row in self.matrix for cell in row)

    def prepare_cells_to_move(self) -> None:
        """Cleanup cells' flags."""
        for row in self.matrix:
            for cell in row:
                cell.added = False
                cell.moved = False
                cell.new = False


def draw_matrix(window: "curses._CursesWindow", matrix: list[list[Cell]]) -> None:
    """
    Draw the matrix in its window.

    New cells are drawn in bold.
    """
    cell_delimiter = f"{'-' * CELL_WIDTH}+"
    delimiter = f"+{cell_delimiter * len(matrix[0])}"
    window.erase()
    window.addstr(f"{delimiter}\n")
    for row in matrix:
        window.addstr("|")
        for cell in row:
            value = f"{str(cell) if cell else ' ':^{CELL_WIDTH}}"
            if cell.new:
                window.addstr(value, curses.A_BOLD)
            else:
                window.addstr(value)
            window.addstr("|")
        window.addstr("\n")
        window.addstr(f"{delimiter}\n")
    window.refresh()


def draw_score(window: "curses._CursesWindow", value: int) -> None:
    """Draw the score in its window."""
    window.erase()
    window.addstr(f"Score: {value}")
    window.refresh()


def main(stdscr: "curses._CursesWindow") -> tuple[bool, int]:
    """
    Set up windows and run the game loop.

    Returns:
        game_over: True is no cell can move
        score: The final game score
    """
    curses.curs_set(0)
    matrix = Matrix()

    stdscr.clear()
    matrix_win_width = CELL_WIDTH * MATRIX_WIDTH + MATRIX_WIDTH + 2
    matrix_win_height = MATRIX_HEIGHT * 2 + 2

    matrix_win = stdscr.derwin(matrix_win_height, matrix_win_width, 0, 0)
    score_win_width = SCORE_WIDTH + 7
    score_win = stdscr.derwin(
        matrix_win_height, score_win_width, 0, matrix_win_width + 1
    )

    draw_score(score_win, matrix.score)
    draw_matrix(matrix_win, matrix.matrix)

    while True:
        key = stdscr.getch()
        if key == ord("q"):
            break  # Exit the while loop
        if key == curses.KEY_UP:
            matrix.move(Direction.UP)
        elif key == curses.KEY_DOWN:
            matrix.move(Direction.DOWN)
        elif key == curses.KEY_RIGHT:
            matrix.move(Direction.RIGHT)
        elif key == curses.KEY_LEFT:
            matrix.move(Direction.LEFT)
        draw_matrix(matrix_win, matrix.matrix)
        draw_score(score_win, matrix.score)
        if matrix.is_full():
            # Game over!
            break
    return matrix.is_full(), matrix.score


if __name__ == "__main__":
    game_over, score = curses.wrapper(main)
    if game_over:
        print("Game over!")
    print(f"Game ended, your score is {score}")
