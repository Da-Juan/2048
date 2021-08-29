#!/usr/bin/env python3
import random
from dataclasses import dataclass
from enum import Enum, auto
from typing import Union

MATRIX_HEIGHT = 4
MATRIX_WIDTH = 4
CELL_WIDTH = 6


class Direction(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()


@dataclass
class Cell:
    value: int = 0
    added: bool = False
    moved: bool = False
    new: bool = False

    def __str__(self) -> str:
        return f"{self.value}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, (int, Cell)):
            return NotImplemented
        return self.value == (other if isinstance(other, int) else other.value)

    def __add__(self, v: Union[int, "Cell"]) -> None:
        add_value = v if isinstance(v, int) else v.value
        if self.value != 0 and add_value != 0:
            self.added = True
        self.moved = True
        self.value += add_value

    def __iadd__(self, v: Union[int, "Cell"]) -> "Cell":
        self.__add__(v)
        return self

    def __bool__(self) -> bool:
        return not self.value == 0


class Matrix:
    def __init__(self) -> None:
        random.seed()

        matrix = []
        for _ in range(0, MATRIX_HEIGHT):
            matrix.append([Cell() for _ in range(0, MATRIX_WIDTH)])

        self.matrix = matrix
        self.add_new_value()
        self.add_new_value()
        self.score = 0

    @property
    def _delimiter(self) -> str:
        cell_delimiter = f"{'-' * CELL_WIDTH}+"
        return f"+{cell_delimiter * len(self.matrix[0])}"

    def add_new_value(self) -> None:
        free_cells = self.find_value(0)
        if not free_cells:
            return
        x, y = random.choice(free_cells)
        self.matrix[y][x].value = random.choices((2, 4), (80, 20))[0]
        self.matrix[y][x].new = True

    def is_full(self) -> bool:
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
        coordinates = []
        for y, row in enumerate(self.matrix):
            for x, cell in enumerate(row):
                if cell == value:
                    coordinates.append((x, y))
        return coordinates

    def get_neighbors(self, x: int, y: int) -> tuple[int, ...]:
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

    def print(self) -> None:
        print(self._delimiter)
        for row in self.matrix:
            row_to_print = "|"
            for cell in row:
                if cell.new:
                    row_to_print += "\033[1m"
                row_to_print += f"{str(cell) if cell else ' ':^{CELL_WIDTH}}"
                if cell.new:
                    row_to_print += "\033[0m"
                    cell.new = False
                row_to_print += "|"
            print(row_to_print)
            print(self._delimiter)

    def rotate_cw(self) -> None:
        rotated = list(zip(*reversed(self.matrix)))
        self.matrix = [list(element) for element in rotated]

    def rotate_ccw(self) -> None:
        rotated = list(zip(*reversed(self.matrix)))
        self.matrix = [list(element)[::-1] for element in rotated][::-1]

    def move(self, direction: Direction) -> None:
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
            self.clean_cells_after_move()
            self.add_new_value()
        else:
            print("Nothing moved")

    def move_cell_to_right(self, x: int, y: int) -> None:
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
        return any([cell.moved for row in self.matrix for cell in row])

    def clean_cells_after_move(self) -> None:
        for y in range(0, MATRIX_HEIGHT):
            for x in range(0, MATRIX_WIDTH):
                self.matrix[y][x].added = False
                self.matrix[y][x].moved = False


def main() -> None:
    matrix = Matrix()
    matrix.print()
    while True:
        d = input("Direction: ")
        if d == "u":
            matrix.move(Direction.UP)
        if d == "d":
            matrix.move(Direction.DOWN)
        if d == "r":
            matrix.move(Direction.RIGHT)
        if d == "l":
            matrix.move(Direction.LEFT)
        if d == "q":
            break
        matrix.print()
        print(f"Score: {matrix.score}")
        if matrix.is_full():
            print("Game over!")
            break


if __name__ == "__main__":
    main()
