"""
The Brandeis Quant Club ML/AI Competition (November 2023)

Author: @Ephraim Zimmerman
Email: quants@brandeis.edu
Website: brandeisquantclub.com; quants.devpost.com

Description:

For any technical issues or questions please feel free to reach out to
the "on-call" hackathon support member via email at quants@brandeis.edu

Website/GitHub Repository:
You can find the latest updates, documentation, and additional resources for this project on the
official website or GitHub repository: https://github.com/EphraimJZimmerman/chess_hackathon_23

License:
This code is open-source and released under the MIT License. See the LICENSE file for details.
"""
import random
import chess
import time
from typing import Iterator
from contextlib import contextmanager
import test_bot
import numpy as np
import requests


@contextmanager
def game_manager() -> Iterator[None]:
    """Creates context for game."""

    print("===== GAME STARTED =====")
    ping: float = time.perf_counter()
    try:
        # DO NOT EDIT. This will be replaced w/ judging context manager.
        yield
    finally:
        pong: float = time.perf_counter()
        total = pong - ping
        print(f"Total game time = {total:.3f} seconds")
    print("===== GAME ENDED =====")


class Bot:
    def __init__(self, fen=None):
        self.board = chess.Board(fen if fen else "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

    def check_move_is_legal(self, initial_position, new_position) -> bool:

        """
            To check if, from an initial position, the new position is valid.

            Args:
                initial_position (str): The starting position given chess notation.
                new_position (str): The new position given chess notation.

            Returns:
                bool: If this move is legal
        """

        return chess.Move.from_uci(initial_position + new_position) in self.board.legal_moves

    def next_move(self) -> str:
        """
            The main call and response loop for playing a game of chess.

            Returns:
                str: The current location and the next move.
        """

        # Assume that you are playing an arbitrary game. This function, which is
        # the core "brain" of the bot, should return the next move in any circumstance.

        # Gives a pre-set first move, a "book opening"
        if self.board.fen() == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1":
            return "d2d4"
        if self.board.fen() == "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1":
            return "e7e5"
        if self.board.fen() == "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq - 0 1":
            return "d7d5"

        possible_moves = [_ for _ in self.board.legal_moves]
        best_move = [[], -1000]
        evaluation = 0

        # looks at the evaluation of the position following each move
        for move in possible_moves:
            new_Board = self.board.copy()
            new_Board.push(move)

            # depth is set to 4.5
            evaluation = self.eval_position(new_Board, 4.5)

            # makes clack player play for black's advantage
            if self.board.turn == chess.BLACK:
                evaluation *= -1

            # finds best move
            if evaluation > best_move[1]:
                best_move = [[move], evaluation]
            elif evaluation == best_move[1]:
                best_move[0].append(move)

        # randomizes across equally good moves
        move = random.choice(best_move[0])
        print("My move: " + move.uci())
        return move.uci()

    # gives a 'score' for each position on how good it is for white
    def eval_position(self, position, depth=0.0):

        # prioritizes checkmate
        if position.is_checkmate():
            if position.turn == chess.WHITE:
                return -100
            else:
                return 100
        if position.is_insufficient_material():
            return 0
        if position.is_stalemate():
            return 0

        # base case
        if depth <= 0:
            # evaluates material advantage
            white_material = 0
            black_material = 0
            piece_values = {'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'p': -1, 'n': -3, 'b': -3, 'r': -5, 'q': -9}
            board_full = position.fen()
            board = board_full[0:board_full.index(' ')]
            rank = 8
            for i in board:
                if i in piece_values.keys():
                    if piece_values[i] > 0:
                        white_material += piece_values[i]

                        # gives extra points for pushing pawns
                        if piece_values[i] == 1:
                            white_material += ((.1 * rank) - .45)
                    else:
                        black_material -= piece_values[i]
                        if piece_values[i] == 1:
                            black_material += (.45 - (.1 * rank))

                if i == "/":
                    rank -= 1

            evaluation = np.sqrt(white_material) - np.sqrt(black_material)

            return evaluation

        else:
            # lists the three different types of moves
            boring_moves = []
            checks = []
            captures = []
            for move in position.legal_moves:
                if position.gives_check(move):
                    checks.append(move)
                elif position.is_capture(move):
                    captures.append(move)
                else:
                    boring_moves.append(move)

            # determines how far to look based on move type
            evaluations = []
            for move in checks:
                new_board = position.copy()
                new_board.push(move)
                evaluations.append(self.eval_position(new_board, depth - .5))
            for move in captures:
                new_board = position.copy()
                new_board.push(move)
                evaluations.append(self.eval_position(new_board, depth - 2))

            if depth > 2:
                for move in boring_moves:
                    new_board = position.copy()
                    new_board.push(move)
                    evaluations.append(self.eval_position(new_board, depth - 3))
            else:
                evaluations.append(self.eval_position(position, -1))

            # assumes player will always make their best available move
            if position.turn == chess.WHITE:
                return np.max(evaluations)
            else:
                return np.min(evaluations)

# Add promotion stuff

# if __name__ == "__main__":
if True:

    chess_bot = Bot()  # you can enter a FEN here, like Bot("...")
    with game_manager():

        """
        
        Feel free to make any adjustments as you see fit. The desired outcome 
        is to generate the next best move, regardless of whether the bot 
        is controlling the white or black pieces. The code snippet below 
        serves as a useful testing framework from which you can begin 
        developing your strategy.

        """

        playing = True

        while playing:
            if chess_bot.board.turn:
                chess_bot.board.push_san(test_bot.get_move(chess_bot.board))
            else:
                chess_bot.board.push_san(chess_bot.next_move())
            print(chess_bot.board, end="\n\n")

            if chess_bot.board.is_game_over():
                if chess_bot.board.is_stalemate():
                    print("Is stalemate")
                elif chess_bot.board.is_insufficient_material():
                    print("Is insufficient material")

                # EX: Outcome(termination=<Termination.CHECKMATE: 1>, winner=True)
                print(chess_bot.board.outcome())

                playing = False
