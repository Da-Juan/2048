#!/usr/bin/env python3
"""My take on the 2048 game."""

from game import Game


if __name__ == "__main__":
    with Game() as game:
        game_over, score = game.run()
    if game_over:
        print("Game over!")
    print(f"Game ended, your score is {score}")
