import sys
sys.path.insert(0, '../')

from state_superclass import CheckersGameState
from structs import *

FRESH_BOARD_REPR = """+b+b+b+b
b+b+b+b+
+b+b+b+b
-+-+-+-+
+-+-+-+-
w+w+w+w+
+w+w+w+w
w+w+w+w+

Black's move"""

class Bitboard32State(CheckersGameState):
    """Uses 32-slot representation of checkerboards."""

    class Move:
        def __init__(self, p_move=None):
            self.move = p_move
            if not self.move:
                self.move = state32.Move_alloc()
                state32.Move_init(self.move, 0)

        def __str__(self):
            return state32.Move_to_string(self.move).decode("utf-8")

    def __init__(self, blackPieces=0x00000fff, whitePieces=0xfff00000, kingPieces=0x00000000, isWhite=False, board=None):
        self.board = board
        if not self.board:
            self.board = state32.Board_alloc()
            if (isWhite):
                plyr = c_ushort(1)
            else:
                plyr = c_ushort(0)
            state32.Board_init(self.board, blackPieces, whitePieces, kingPieces, plyr)

    def __str__(self):
        return state32.Board_to_string(self.board).decode("utf-8")

    def from_string(self, board_string=FRESH_BOARD_REPR):
        new_board = state32.Board_from_string(create_string_buffer(board_string.encode("utf-8")))
        return Bitboard32State(0, 0, 0, False, new_board)

    def actions(self):
        movelist = pointer(pointer(MOVE()))
        numMoves = c_int(0)
        movelist = state32.actions(self.board, byref(numMoves))
        moves = []
        for i in range(0, numMoves.value):
            newMove = Bitboard32State.Move(movelist[i])
            moves.append(newMove)
        return iter(moves)

    def result(self, move=None):
        if not move:
            return self
        new_board = state32.result(self.board, move.move)
        return Bitboard32State(0, 0, 0, False, new_board)

    def player(self):
        return state32.player(self.board).decode("utf-8")
