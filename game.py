"""Game engine."""
import curses
from typing import Any

from direction import Direction

from matrix import Matrix

MATRIX_HEIGHT = 4
MATRIX_WIDTH = 4
CELL_WIDTH = 6
SCORE_WIDTH = 6


class Game:
    """Main game class."""

    def __init__(self):
        """Initialize the engine."""
        self.matrix = Matrix(MATRIX_WIDTH, MATRIX_HEIGHT)

        self._stdscr = curses.initscr()
        self._stdscr.clear()
        self._stdscr.keypad(True)

        self.matrix_win_width = CELL_WIDTH * MATRIX_WIDTH + MATRIX_WIDTH + 2
        self.matrix_win_height = MATRIX_HEIGHT * 2 + 2

        self.matrix_win = self._stdscr.derwin(
            self.matrix_win_height, self.matrix_win_width, 0, 0
        )
        self.score_win_width = SCORE_WIDTH + 7
        self.score_win = self._stdscr.derwin(
            self.matrix_win_height, self.score_win_width, 0, self.matrix_win_width + 1
        )

    def __enter__(self):
        """Initialize curses."""
        curses.curs_set(0)
        curses.cbreak()
        curses.noecho()

        self.draw_score()
        self.draw_matrix()

        return self

    def __exit__(self, exc_type: Exception, exc_value: Any, exc_traceback: Any):
        """Cleanup curses."""
        curses.nocbreak()
        self._stdscr.keypad(0)
        curses.echo()
        curses.endwin()

    def run(self):
        """Run the game loop."""
        while True:
            key = self._stdscr.getch()
            if key == ord("q"):
                break  # Exit the while loop
            if key == curses.KEY_UP:
                self.matrix.move(Direction.UP)
            elif key == curses.KEY_DOWN:
                self.matrix.move(Direction.DOWN)
            elif key == curses.KEY_RIGHT:
                self.matrix.move(Direction.RIGHT)
            elif key == curses.KEY_LEFT:
                self.matrix.move(Direction.LEFT)
            self.draw_matrix()
            self.draw_score()
            if self.matrix.is_full():
                # Game over!
                break
        return self.matrix.is_full(), self.matrix.score

    def draw_matrix(self) -> None:
        """
        Draw the matrix in its window.

        New cells are drawn in bold.
        """
        cell_delimiter = f"{'-' * CELL_WIDTH}+"
        delimiter = f"+{cell_delimiter * len(self.matrix.matrix[0])}"
        self.matrix_win.erase()
        self.matrix_win.addstr(f"{delimiter}\n")
        for row in self.matrix.matrix:
            self.matrix_win.addstr("|")
            for cell in row:
                value = f"{str(cell) if cell else ' ':^{CELL_WIDTH}}"
                if cell.new:
                    self.matrix_win.addstr(value, curses.A_BOLD)
                else:
                    self.matrix_win.addstr(value)
                self.matrix_win.addstr("|")
            self.matrix_win.addstr("\n")
            self.matrix_win.addstr(f"{delimiter}\n")
        self.matrix_win.refresh()

    def draw_score(self) -> None:
        """Draw the score in its window."""
        self.score_win.erase()
        self.score_win.addstr(f"Score: {self.matrix.score}")
        self.score_win.refresh()
