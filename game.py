"""Game engine."""
import curses
import datetime
import pathlib
import sqlite3
from types import TracebackType

from direction import Direction
from matrix import Matrix

MATRIX_HEIGHT = 4
MATRIX_WIDTH = 4
CELL_WIDTH = 6
SCORE_WIDTH = 6
SCORE_DB = "~/.2048.db"


class Game:
    """Main game class."""

    def __init__(self: "Game") -> None:
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

    def __enter__(self: "Game") -> "Game":
        """Initialize curses."""
        curses.curs_set(0)
        curses.cbreak()
        curses.noecho()

        self.load_scores()
        self.draw_score()
        self.draw_matrix()

        return self

    def __exit__(
        self: "Game",
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        exc_traceback: TracebackType | None,
    ) -> None:
        """Cleanup curses."""
        curses.nocbreak()
        self._stdscr.keypad(False)  # noqa: FBT003
        curses.echo()
        curses.endwin()

        self.save_score()

    def load_scores(self) -> None:
        """Load the list of scores."""
        score_conn = sqlite3.connect(pathlib.Path(SCORE_DB).expanduser())
        cursor = score_conn.cursor()
        self.scores = []
        try:
            results = cursor.execute("SELECT score FROM scores ORDER BY score DESC")
            self.scores = [result[0] for result in results.fetchall()]
        except sqlite3.OperationalError:
            cursor.execute("CREATE TABLE scores (date date, score int)")

    def save_score(self) -> None:
        """Save the current game score."""
        if self.matrix.score == 0:
            return
        score_conn = sqlite3.connect(pathlib.Path(SCORE_DB).expanduser())
        cursor = score_conn.cursor()
        cursor.execute(
            "INSERT INTO scores VALUES (?, ?)",
            (datetime.datetime.now(tz=datetime.UTC), self.matrix.score),
        )
        score_conn.commit()

    def get_score_position(self) -> int:
        """Get the rank of the current game's score."""
        if not self.scores:
            return 1

        if self.matrix.score > self.scores[0]:
            return 1

        for index, score in enumerate(self.scores):
            if self.matrix.score >= score:
                return index + 1

        return 0

    def run(self: "Game") -> tuple[bool, int, int]:
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
        return self.matrix.is_full(), self.matrix.score, self.get_score_position()

    def draw_matrix(self: "Game") -> None:
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

    def draw_score(self: "Game") -> None:
        """Draw the score in its window."""
        self.score_win.erase()
        score = f"Score: {self.matrix.score}"
        if self.scores and self.matrix.score > self.scores[0]:
            score += f"\n(+{self.matrix.score - self.scores[0]})"
        self.score_win.addstr(score)
        self.score_win.refresh()
