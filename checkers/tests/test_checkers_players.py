import unittest

from checkers.heuristics import BoardEvaluator
from checkers.state import Bitboard32State as BoardState

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

    def test_board_evaluator_sanity(self):
        my_weights = {"count_friends" : 5,
                      "count_foes" : -5,
                      "count_friends_kings" : 2,
                      "count_foes_kings" : -2}

        be = BoardEvaluator(my_weights)
        self.assertEqual(be(BoardState()),
                         0)  # should be balanced

        self.assertEqual(be(BoardState.from_string(ENDGAME_BOARD)),
                         10 - 15 + 2 - 4)
        self.assertEqual(
            be(BoardState.from_string(ENDGAME_BOARD.replace("Black",
                                                            "White"))),
            -be(BoardState.from_string(ENDGAME_BOARD)))
