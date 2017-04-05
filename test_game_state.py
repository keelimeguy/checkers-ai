#!/usr/bin/env python3

"""Unit tests for game state representations"""

from __future__ import print_function  # in case you're using python2
import sys  # to print an error in a certain case
import unittest

# put a line to import your game state implementation here
from samuel_state import SamuelGameState
from state_superclass import CheckersGameState, parse_board_string
from EightXEight import EightXEightGameState


FRESH_BOARD_REPR = """+b+b+b+b
b+b+b+b+
+b+b+b+b
-+-+-+-+
+-+-+-+-
w+w+w+w+
+w+w+w+w
w+w+w+w+

Black's move"""



class CheckersGameStateTestCase(unittest.TestCase):
    """Test cases for checker boards. 

    You can subclass this to test your own board.

    This does test a particular board, because it will run and fail without a
    working class. (This is easy to demonstrate at the time of writing!)"""

    def setUp(self):
        """Overwrite this in subclass to test a different class

        You can also add more tests in a subclass if you feel inspired.

        FYI, the creators of unittest use camel-casing, but for functions and
        methods, the usual convention is to use underscores.
        """
        self.state_class = SamuelGameState

    def test_parsing_from_string(self):
        """If only to facilitate testing, it's nice to parse the string version
        of a board into an actual board.
        """
        self.assertEqual(str(self.state_class.from_string(FRESH_BOARD_REPR)),
                         FRESH_BOARD_REPR)

    def test_initial_state_player(self):
        """Black goes first"""
        fresh_board = self.state_class()

        self.assertEqual(fresh_board.player(),
                         "Black")

    def test_initial_state_to_string(self):
        """Make sure the to_string (__str__) of the initial board works"""
        # `str(x)` is equivalent to `x.__str__()`
        self.assertEqual(str(self.state_class()),
                         FRESH_BOARD_REPR)

    def test_initial_state_actions(self):
        """Sanity check for the available actions of the initial state"""
        # put the possible actions in a list and make sure its length is 7
        self.assertEqual(len([*self.state_class().actions()]),
                         7)

    def test_action_results(self):
        """Make some random moves and do some sanity checks"""
        current = self.state_class()


        for _ in range(10):  # i.e. repeat 10 times
            # Note that the game can't end in 10 moves, so if it does,
            # then something is terribly wrong
            try:
                action = next(current.actions())
            except StopIteration:
                raise AssertionError(
                    "No actions for early board state:\n{}\nof type {}".format(
                        str(current)), type(current))
            next_state = current.result(action)
            # Now test some basic stuff that makes sense
            self.assertIsInstance(next_state, CheckersGameState)
            self.assertNotEqual(next_state, current)
            self.assertNotEqual(next_state.player(), current.player())
            self.assertIn(next_state.player(), set(["Black", "White"]))
            self.assertNotEqual(str(next_state), str(current))
            # We could also count the number of pieces (via the string
            # representation) to make sure that, e.g., players aren't losing
            # pieces on their own turns, or gaining pieces for that matter.


    def test_king_jump_option_computation(self):
        """Correctly parse a board (with from_string) and find four possible
        jump sequences. Also accurately represent double-jump moves in server
        format.
        """
        board_string = """
+b+-+-+-
-+b+-+-+
+-+W+-+-
-+b+b+-+
+-+-+-+-
-+b+b+b+
+-+-+-+-
-+-+-+-+

White's move""".strip()  # strip() removes the initial newline # (which is just
        #                  for readability)

        moves = sorted(["(5:3):(3:1):(1:3):(3:5):(5:3)",
                        "(5:3):(3:1):(1:3):(3:5):(1:7)",
                        "(5:3):(3:5):(1:7)",
                        "(5:3):(3:5):(1:3):(3:1):(5:3)"])
        acts = self.state_class.from_string(board_string).actions()
        # The lists (which have both been sorted lexicographically) should be
        # the same
        self.assertEqual(sorted([str(act) for act in acts]),
                         moves)

    def test_jump_into_king_end_turn(self):
        """According to rules: when your piece becomes a king, your turn ends there.
           Let's check that we don't keep jumping
        """
        board_string = """
+-+-+-+-
-+-+-+-+
+-+-+-+-
-+-+-+-+
+-+-+-+-
-+-+b+b+
+-+w+w+-
-+-+-+-+

Black's move""".strip()  # strip() removes the initial newline # (which is just
        #                  for readability)

        moves = sorted(["(2:6):(0:4)",
                        "(2:4):(0:2)",
                        "(2:4):(0:6)"])
        acts = self.state_class.from_string(board_string).actions()
        # The lists (which have both been sorted lexicographically) should be
        # the same
        self.assertEqual(sorted([str(act) for act in acts]),
                         moves)

    def test_jump_forward_only(self):
        """Test that we only jump forwards, not backwards
        """
        board_string = """
+-+-+-+-
-+-+-+-+
+-+-+-+-
-+-+b+b+
+-+w+w+-
-+-+-+-+
+-+-+-+-
-+-+-+-+

Black's move""".strip()  # strip() removes the initial newline # (which is just
        #                  for readability)

        moves = sorted(["(4:6):(2:4)",
                        "(4:4):(2:2)",
                        "(4:4):(2:6)"])
        acts = self.state_class.from_string(board_string).actions()
        # The lists (which have both been sorted lexicographically) should be
        # the same
        self.assertEqual(sorted([str(act) for act in acts]),
                         moves)

class EightByEightTestCase(CheckersGameStateTestCase):
    def setUp(self):
        self.state_class = EightXEightGameState


class ParserHelperTestCase(unittest.TestCase):
    """Tests the thing that makes parsing boards easier"""

    def test_parse_board_string(self):
        """Test the function that helps parse boards from strings"""
        example = """
+-+-+-+w
-+-+-+-+
+-+W+-+-
-+-+-+-+
+-+-+-+-
-+-+-+-+
+-+-+b+B
-+-+-+-+

White's move
""".strip()
        pieces, player = parse_board_string(example)
        self.assertEqual(len(pieces), 4)
        self.assertIn((1, 7, 'B'), pieces)
        self.assertIn((1, 5, 'b'), pieces)
        self.assertIn((5, 3, 'W'), pieces)
        self.assertIn((7, 7, 'w'), pieces)

class KeelinGameStateTestCase(CheckersGameStateTestCase):
    """Test keelin's game state"""

    def setUp(self):
        self.state_class = KeelinGameState

if __name__ == "__main__":
    unittest.main()
