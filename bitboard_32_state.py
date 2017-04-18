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

#We will use heuristics as described in the Warsaw Paper

    def count_friends(self):
        if self.board.contents.plyr:
            friends = self.board.contents.w
        else:
            friends = self.board.contents.b
        return state32_lib.count_bits(friends)

    def count_friends_pawns(self):
	if self.board.contents.plyr:
	    friends = self.board.contents.w
	else:
	    friends = self.board.contents.b
	return state32_lib.count_bits(friends) - state32_lib.count_bits(friends & self.board.contents.k)
   
    def count_foes(self):
        if self.board.contents.plyr:
            foes = self.board.contents.b
        else:
            foes = self.board.contents.w
        return state32_lib.count_bits(foes)

    def count_foes_pawns(self):
        if self.board.contents.plyr:
            foes = self.board.contents.b
        else:
            foes = self.board.contents.w
        return state32_lib.count_bits(foes) - state32_lib.count_bits(friends & self.board.contents.k)
   
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

    def count_safe_friends_pawns(self):
        if self.board.contents.plyr:
            friends = self.board.contents.w
        else:
            friends = self.board.contents.b
        return state32_lib.count_bits(friends & 0xf818181f & ~self.board.contents.k)

    def count_safe_foes_pawns(self):
        if self.board.contents.plyr:
            foes = self.board.contents.b
        else:
            foes = self.board.contents.w
        return state32_lib.count_bits(foes & 0xf818181f & ~self.board.contents.k)

    def count_safe_friends_kings(self):
        if self.board.contents.plyr:
            friends = self.board.contents.w
        else:
            friends = self.board.contents.b
        return state32_lib.count_bits(friends & 0xf818181f & self.board.contents.k)

    def count_safe_foes_kings(self):
        if self.board.contents.plyr:
            foes = self.board.contents.b
        else:
            foes = self.board.contents.w
        return state32_lib.count_bits(foes & 0xf818181f & self.board.contents.k)

    def count_movable_friends_pawns(self):

    def count_movable_foes_pawns(self):

    def count_movable_friends_kings(self):

    def count_movable_foes_kings(self):
   
    def aggregate_distance_promotion_friends(self):
    
    def aggregate_distance_promotion_foes(self):

    def count_unoccupied_promotion_friends(self):

    def count_unoccupied_promotion_foes(self):

    def count_defender_pieces_friends(self):

    def count_defender_pieces_foes(self):

    def count_attack_pawns_friends(self):

    def count_attack_pawns_foes(self):

    def count_center_pawns_friends(self):

    def count_center_pawns_foes(self):

    def count_center_kings_friends(self):

    def count_center_kings_foes(self):
	if self.board.contents.plyr:
	    foes = self.board.contents.b
	else:
	    foes = self.board.contents.w
	return state32_lib.count_bits(foes & 0x00666600 & self.board.contents.k)

    def count_diagonalmain_pawns_friends(self):

    def count_diagonalmain_pawns_foes(self):

    def count_diagonalmain_kings_friends(self):

    def count_diagonalmain_kings_foes(self):

    def count_diagonaldouble_pawns_friends(self):

    def count_diagoanldouble_pawns_foes(self):

    def count_diagonaldouble_kings_friends(self):

    def count_diagonaldouble_kings_foes(self):

    def count_loner_pawns_friends(self):

    def count_loner_pawns_foes(self):

    def count_loner_kings_friends(self):

    def count_loner_kings_foes(self):

    def count_holes_friends(self):

    def count_holes_foes(self):

    def triangle_friends(self):

    def triangle_foes(self):

    def oreo_friends(self):

    def oreo_foes(self):

    def bridge_friends(self):

    def bridge_foes(self):

    def dog_friends(self):

    def dog_foes(self):

    def pawn_corner_friends(self):

    def pawn_corner_foes(self):

    def king_corner_friends(self):

    def king_corner_foes(self):

  

    def difference_pieces(self):
	if self.board.contents.plyr:
	    foes = self.board.contents.b
	    friends = self.baord.contents.w
	else:
	    foes = self.board.contents.w
	    friends = self.board.contents.b
	return state32_lib.count_bits(friends) - state32_lib.count_bits(foes)


