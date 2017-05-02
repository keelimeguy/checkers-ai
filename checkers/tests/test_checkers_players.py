import unittest

from checkers.heuristics import BoardEvaluator
from checkers.state import Bitboard32State as BoardState

try:
    from math import inf
except ImportError:
    inf = float('inf')

ENDGAME_BOARD = """+-+-+-+-
-+-+-+-+
+W+-+-+-
-+-+W+B+
+w+-+-+-
-+-+-+-+
+-+b+-+-
-+-+-+-+

Black's move"""


class BoardEvaluatorTestCase(unittest.TestCase):

    def setUp(self):
        self.weights = {"count_friends" : 5,
                      "count_foes" : -5,
                      "count_friends_kings" : 2,
                      "count_foes_kings" : -2}

        self.be = BoardEvaluator(self.weights)


    def test_board_evaluator_sanity(self):
        self.assertEqual(self.be(BoardState()),
                         0)  # should be balanced

        self.assertEqual(self.be(BoardState.from_string(ENDGAME_BOARD)),
                         10 - 15 + 2 - 4)
        self.assertEqual(
            self.be(BoardState.from_string(ENDGAME_BOARD.replace("Black",
                                                                 "White"))),
            -self.be(BoardState.from_string(ENDGAME_BOARD)))

    def test_win_loss_values(self):
        black_lost = ENDGAME_BOARD.replace("+b", "+-").replace("+B", "+-")
        self.assertEqual(self.be(BoardState.from_string(black_lost)),
                         -inf)
        self.assertEqual(self.be(BoardState.from_string(black_lost.replace(
            "Black", "White"))),
                         inf)  # White won, rather than Black losing
        black_won = black_lost.replace("W", "w").replace("w", "B")
        self.assertEqual(self.be(BoardState.from_string(black_won)),
                         inf)
        self.assertEqual(self.be(BoardState.from_string(black_won.replace(
            "Black", "White"))),
                         -inf)

