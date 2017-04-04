#!/usr/bin/env python3

"""Unit tests for game state representations"""

from __future__ import print_function  # in case you're using python2
import sys  # to print an error in a certain case
import unittest

# put a line to import your game state implementation here
from samuel_state import SamuelGameState
from state_superclass import CheckersGameState

FRESH_BOARD_REPR = """-b-b-b-b
b-b-b-b-
-b-b-b-b
--------
--------
w-w-w-w-
-w-w-w-w
w-w-w-w-

Black's move"""

class CheckersGameStateTestCase(unittest.TestCase):

    def setUp(self):
        """Overwrite this in subclass to test a different class

        You can also add more tests in a subclass if you feel inspired.

        FYI, the creators of unittest use camel-casing, but for functions and
        methods, the usual convention is to use underscores.
        """
        self.state_class = SamuelGameState

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
