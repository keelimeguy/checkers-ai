import unittest

from checkers.heuristics import BoardEvaluator
from checkers.state import Bitboard32State as BoardState
from checkers.alphabeta import AlphaBeta

from math import inf

W_WIN_IN_3 = """
+B+-+-+-
-+-+-+-+
+W+W+-+-
-+-+-+-+
+-+-+-+-
-+-+-+-+
+-+-+-+-
-+-+-+-+

White's move""".strip()

# W_WIN_IN_3 = """
# +B+-+-+-
# -+-+-+-+
# +W+W+-+-
# -+-+-+-+
# +-+-+-+-
# -+-+-+-+
# +-+-+-+-
# -+-+-+-+

# White's move""".strip()


class AlphaBetaTestCase(unittest.TestCase):

    def setUp(self):
        self.heval = BoardEvaluator({}, sanity_check=False)

    def test_win_in_3(self):
        """AlphaBeta with no weights should figure this out"""
        b = BoardState.from_string(W_WIN_IN_3)

        searcher = AlphaBeta(self.heval, default_depth=3)
        self.assertEqual(searcher.ab_dfs(b), inf)


        # This next part fails if intermediate results are not in the cache.
        next_board = b.result(b.Move.from_string("(5:1):(6:0)"))

        self.assertIn((next_board, False), searcher.cache)
                      # msg="\n".join("{}, {}".format(*x)
                      #               for x in searcher.cache.keys()))

        self.assertEqual(searcher.ab_dfs(next_board,
                                         maximum=False,
                                         depth=0),
                         inf)
                         # msg=f"cache size: {len(searcher.cache)}")


    def test_no_win_in_6(self):

        searcher = AlphaBeta(self.heval)
        searcher.default_depth = 6
        # don't find a win/loss in 6 moves
        self.assertNotIn(searcher.ab_dfs(BoardState()),
                         {inf, -inf})

if __name__ == '__main__':
    unittest.main()
