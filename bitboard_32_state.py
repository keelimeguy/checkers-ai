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
                self.move = state32_lib.Move_alloc()
                state32_lib.Move_init(self.move, 0)

        def __str__(self):
            return state32_lib.Move_to_string(self.move).decode("utf-8")

    def __init__(self, black_pieces=0x00000fff, white_pieces=0xfff00000, king_pieces=0x00000000, is_white=False, board=None):
        self.board = board
        if not self.board:
            self.board = state32_lib.Board_alloc()
            if (is_white):
                plyr = c_ushort(1)
            else:
                plyr = c_ushort(0)
            state32_lib.Board_init(self.board, black_pieces, white_pieces, king_pieces, plyr)

    def __str__(self):
        return state32_lib.Board_to_string(self.board).decode("utf-8")

    def from_string(self, board_string=FRESH_BOARD_REPR):
        new_board = state32_lib.Board_from_string(create_string_buffer(board_string.encode("utf-8")))
        return Bitboard32State(0, 0, 0, False, new_board)

    def move_from_string(self, movestr=None):
        if not movestr:
            return None
        return self.Move(state32_lib.Move_from_string(movestr.encode("utf-8")))

    def actions(self):
        return iter(self.list_actions())

    def list_actions(self):
        movelist = pointer(pointer(MOVE()))
        numMoves = c_int(0)
        movelist = state32_lib.actions(self.board, byref(numMoves))
        moves = []
        for i in range(0, numMoves.value):
            newMove = Bitboard32State.Move(movelist[i])
            moves.append(newMove)
        return moves

    def result(self, move=None):
        if not move:
            return self
        new_board = state32_lib.result(self.board, move.move)
        return Bitboard32State(0, 0, 0, False, new_board)

    def player(self):
        return state32_lib.player(self.board).decode("utf-8")

    def count_friends(self):
        if self.board.contents.plyr:
            friends = self.board.contents.w
        else:
            friends = self.board.contents.b
        return state32_lib.count_bits(friends)

    def count_foes(self):
        if self.board.contents.plyr:
            foes = self.board.contents.b
        else:
            foes = self.board.contents.w
        return state32_lib.count_bits(foes)

    def count_crowned_friends(self):
        if self.board.contents.plyr:
            friends = self.board.contents.w
        else:
            friends = self.board.contents.b
        return state32_lib.count_bits(friends & self.board.contents.k)

    def count_crowned_foes(self):
        if self.board.contents.plyr:
            foes = self.board.contents.b
        else:
            foes = self.board.contents.w
        return state32_lib.count_bits(foes & self.board.contents.k)
