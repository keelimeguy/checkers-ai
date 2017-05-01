import unittest

from checkers.heuristics import BoardEvaluator
from checkers.state import Bitboard32State as BoardState
from checkers.alphabeta import AlphaBeta

# from math import inf

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

class AlphaBetaTestCase(unittest.TestCase):

    def setUp(self):
        self.heval = BoardEvaluator({}, sanity_check=False)

    def test_win_in_3(self):
        """AlphaBeta with no weights should figure this out"""
        b = BoardState.from_string(W_WIN_IN_3)

        searcher = AlphaBeta(self.heval)
        searcher.default_depth = 4
        self.assertEqual(searcher.ab_dfs(b), float('inf'))
        # This next part fails if intermediate results are not in the cache.
        self.assertEqual(searcher.ab_dfs(b.result(b.Move.from_string("(5:1):(6:0)")),
                                         maximum=False,
                                         depth=0),
                         float('inf'),
                         msg="{}".format(len(searcher.cache)))


    def test_no_win_in_6(self):

        searcher = AlphaBeta(self.heval)
        searcher.default_depth = 6
        # don't find a win/loss in 6 moves
        self.assertNotIn(searcher.ab_dfs(BoardState()),
                         {float('inf'), float('-inf')})

if __name__ == '__main__':
    unittest.main()
