#!/usr/bin/env python3

"""
It's almost criminal to do this one in pure Python, but here it is in pure
Python.
"""

from state_superclass import CheckersGameState

# Black/White Checkers/Kings
WC = "w"
BC = "b"
WK = "W"
BK = "B"

class SamuelGameState(CheckersGameState):
    """Uses Samuel's 35-slot representation of checkerboards."""

    class Move:
        """An action for a SamuelGameState"""
        # Don't worry about __slots__. It's a pointless optimization.
        # __slots__ = ["orig", "change", "chain"]
        def __init__(self, *sequence):  # , chain=None):
            """Pass a sequence of locations for a piece to visit in sequence,
            including the start and end locations.

            Usually that's just an origin and destination, unless we're jumping
            multiple times.
            """
            self.sequence = sequence

        def __str__(self):
            """Convert to string parsable by server"""
            return ":".join("({}:{})".format(self.server_row(x),
                                             self.server_col(x))
                            for x in self.sequence)

    @staticmethod
    def index_to_std(sam_index):
        """Get from samuel numbering to EDA standard numbering (1-32)

        Untested
        """
        return sam_index - (sam_index // 9)  # len([i for i in [9, 18, 27] if i < sam_index])

    @staticmethod
    def server_row(sam_index):
        # Origin is (0:0), "at lower right from White's perspective"
        """Return row index in range(8)"""
        return 7 - (sam_index << 1) // 9

    @staticmethod
    def server_col(sam_index):
        """Return column index in range(8)"""
        return ((sam_index << 1) % 9) - 1

    @staticmethod
    def samuel_index(serv_row, serv_col):
        """Take a server row and column and return a samuel index"""
        # samuel's 1 is on Black's side, but server 0 is on White's side
        serv_row = 7 - serv_row
        return (1 + 9 * serv_row + serv_col) >> 1


    def __init__(self, board=None, black=True):
        """Initialize with board state (array of length 36) and next player
        (True if Black)
        """

        self.board = board

        if not self.board:
            # default is starting board
            # Note that since I want to index from 1, I just have a null first
            # element
            self.board =  [BC] * 14 + [None] * 9 + [WC] * 13
            for i in range(0, 36, 9):
                self.board[i] = None
        self.black = black
        

    @staticmethod
    def horiz_valid(index):
        """Is the index invalid for horizontal reasons (bad column)?"""
        return index % 9

    @staticmethod
    def vert_valid(index):
        """Is the index invalid for vertical reasons (bad row)?"""
        return 0 < index < 36

    @staticmethod
    def valid(index):
        """Is the index valid, i.e. is it really on the board?"""
        return SamuelState.horiz_valid(index) and SamuelState.vert_valid(index)

    @staticmethod
    def neighbors(index):
        cls = SamuelState
        """All valid squares adjacent to the given index"""
        candidates = [index + 5, index +4, index - 4, index - 5]
        if 5 < index < 31:
            # A safe distance from the edge of the board
            return [i for i in candidates if cls.horiz_valid(index)]
        else:
            return [i for i in candidates if cls.valid(index)]

    def from_string(*args, **kwargs):
        raise NotImplementedError()
