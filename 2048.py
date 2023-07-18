#!/usr/bin/env python3
"""My take on the 2048 game."""

from game import Game


def get_suffix(n: int) -> str:
    """Get the ordinal english suffix for a given number."""
    return "th" if 4 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")


if __name__ == "__main__":
    with Game() as game:
        game_over, score, position = game.run()
    if game_over:
        print("Game over!")
    if position > 0:
        print(f"Game ended, your score is {score}.")
        if position == 1:
            print("Congratulations! It's your highest score!")
        else:
            print(f"It's your {position}{get_suffix(position)} best game.")
