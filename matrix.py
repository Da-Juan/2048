"""Game elements."""
import random
from dataclasses import dataclass
from typing import Self

from direction import Direction


@dataclass
class Cell:
    """Matrix's cell."""

    value: int = 0
    added: bool = False
    moved: bool = False
    new: bool = False

    def __str__(self: "Cell") -> str:
        """Sting representation."""
        return str(self.value)

    def __eq__(self: "Cell", other: object) -> bool:
        """Compare cell's value with another cell's value or an integer."""
        if not isinstance(other, int | Cell):
            return NotImplemented
        return self.value == (other if isinstance(other, int) else other.value)

    def __iadd__(self: Self, other: int | Self) -> Self:
        """Inplace add."""
        add_value = other if isinstance(other, int) else other.value
        if self.value != 0 and add_value != 0:
            self.added = True
        self.moved = True
        self.value += add_value
        return self

    def __bool__(self: "Cell") -> bool:
        """Boolean operation."""
        return not self.value == 0


class Matrix:
    """Game matrix."""

    def __init__(self: "Matrix", width: int, height: int) -> None:
        """Initialize game matrix."""
        random.seed()

        self.width = width
        self.height = height
        self.matrix = [
            [Cell() for _ in range(self.width)] for _ in range(self.height)
        ]
        self.add_new_value()
        self.add_new_value()
        self.score = 0

    def add_new_value(self: "Matrix") -> None:
        """Add a new value, chosen between 2 and 4, to a random free cell if available.

        2 has an 90% chances to be drawn.
        """
        free_cells = self.find_value(0)
        if not free_cells:
            return
        x, y = random.choice(free_cells)
        self.matrix[y][x].value = random.choices((2, 4), (9, 1))[0]
        self.matrix[y][x].new = True

    def is_full(self: "Matrix") -> bool:
        """Check if the matrix has empty (zero) cells or if cells can move."""
        if self.find_value(0):
            return False
        for y in range(0, self.height):
            for x in range(0, self.width):
                if self.matrix[y][x] == 0:
                    continue
                if self.matrix[y][x].value in self.get_neighbors(x, y):
                    return False
        return True

    def find_value(self: "Matrix", value: int) -> list[tuple[int, int]]:
        """Get the cells' coordinates of a given value."""
        coordinates = []
        for y, row in enumerate(self.matrix):
            for x, cell in enumerate(row):
                if cell == value:
                    coordinates.append((x, y))
        return coordinates

    def get_neighbors(self: "Matrix", x: int, y: int) -> tuple[int, ...]:
        """Get values of the target cell's neighbors(N, S, E, W)."""
        neighbors = [0, 0, 0, 0]
        if y > 0:
            neighbors[0] = self.matrix[y - 1][x].value
        if y < self.height - 1:
            neighbors[1] = self.matrix[y + 1][x].value
        if x < self.width - 1:
            neighbors[2] = self.matrix[y][x + 1].value
        if x > 0:
            neighbors[3] = self.matrix[y][x - 1].value
        return tuple(neighbors)

    def rotate_cw(self: "Matrix") -> None:
        """Rotate the matrix 90° clockwise."""
        rotated = list(zip(*reversed(self.matrix), strict=False))
        self.matrix = [list(element) for element in rotated]

    def rotate_ccw(self: "Matrix") -> None:
        """Rotate the matrix 90° counter clockwise."""
        rotated = list(zip(*reversed(self.matrix), strict=False))
        self.matrix = [list(element)[::-1] for element in rotated][::-1]

    def move(self: "Matrix", direction: Direction) -> None:
        r"""Move cells in the given direction.

        I'm not very good with matrix, I could only figure how to move cells to the right
        so to move in other directions I rotate the matrix then rotate it back. ¯\_(ツ)_/¯
        """
        self.prepare_cells_to_move()
        if direction == Direction.UP:
            self.rotate_cw()
        if direction == Direction.DOWN:
            self.rotate_ccw()
        if direction == Direction.LEFT:
            self.rotate_cw()
            self.rotate_cw()

        self.move_cells()

        if direction == Direction.UP:
            self.rotate_ccw()
        if direction == Direction.DOWN:
            self.rotate_cw()
        if direction == Direction.LEFT:
            self.rotate_ccw()
            self.rotate_ccw()
        if self.has_moved():
            self.add_new_value()

    def move_cells(self: "Matrix") -> None:
        """Browse the matrix and move cells to the right."""
        for y in range(0, self.height):
            for x in reversed(range(0, self.width)):
                if self.matrix[y][x] == 0 or x >= self.width - 1:
                    continue
                self.move_cell_to_right(x, y)

    def move_cell_to_right(self: "Matrix", x: int, y: int) -> None:
        """Move cells to the right.

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
            if x + 1 >= self.width - 1:
                return
            self.move_cell_to_right(x + 1, y)

    def has_moved(self: "Matrix") -> bool:
        """Check if cells have moved in the martix."""
        return any(cell.moved for row in self.matrix for cell in row)

    def prepare_cells_to_move(self: "Matrix") -> None:
        """Cleanup cells' flags."""
        for row in self.matrix:
            for cell in row:
                cell.added = False
                cell.moved = False
                cell.new = False
