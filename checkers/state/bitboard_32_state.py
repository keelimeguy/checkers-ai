from .state_superclass import CheckersGameState
from checkers.c.structs import *

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
        self.c_board = board
        if not self.c_board:
            self.c_board = state32_lib.Board_alloc()
            if (is_white):
                plyr = c_ushort(1)
            else:
                plyr = c_ushort(0)
            state32_lib.Board_init(self.c_board, black_pieces, white_pieces, king_pieces, plyr)

    def __str__(self):
        return state32_lib.Board_to_string(self.c_board).decode("utf-8")

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
        movelist = state32_lib.actions(self.c_board, byref(numMoves))
        moves = []
        for i in range(0, numMoves.value):
            newMove = Bitboard32State.Move(movelist[i])
            moves.append(newMove)
        return moves

    def result(self, move=None):
        if not move:
            return self
        new_board = state32_lib.result(self.c_board, move.move)
        return Bitboard32State(0, 0, 0, False, new_board)

    def player(self):
        return state32_lib.player(self.c_board).decode("utf-8")

    # We will use heuristics as described in the Warsaw Paper

    def count_friends(self):
        if self.c_board.contents.plyr:
            friends = self.c_board.contents.w
        else:
            friends = self.c_board.contents.b
        return state32_lib.count_bits(friends)

    def count_friends_pawns(self):
        if self.c_board.contents.plyr:
            friends = self.c_board.contents.w
        else:
            friends = self.c_board.contents.b
        return state32_lib.count_bits(friends & ~self.c_board.contents.k)

    def count_friends_kings(self):
        if self.c_board.contents.plyr:
            friends = self.c_board.contents.w
        else:
            friends = self.c_board.contents.b
        return state32_lib.count_bits(friends & self.c_board.contents.k)

    def count_foes(self):
        if self.c_board.contents.plyr:
            foes = self.c_board.contents.b
        else:
            foes = self.c_board.contents.w
        return state32_lib.count_bits(foes)

    def count_foes_pawns(self):
        if self.c_board.contents.plyr:
            foes = self.c_board.contents.b
        else:
            foes = self.c_board.contents.w
        return state32_lib.count_bits(foes & ~self.c_board.contents.k)

    def count_foes_kings(self):
        if self.c_board.contents.plyr:
            foes = self.c_board.contents.b
        else:
            foes = self.c_board.contents.w
        return state32_lib.count_bits(foes & self.c_board.contents.k)

    def count_safe_friends_pawns(self):
        if self.c_board.contents.plyr:
            friends = self.c_board.contents.w
        else:
            friends = self.c_board.contents.b
        return state32_lib.count_bits(friends & 0xf818181f & ~self.c_board.contents.k)

    def count_safe_foes_pawns(self):
        if self.c_board.contents.plyr:
            foes = self.c_board.contents.b
        else:
            foes = self.c_board.contents.w
        return state32_lib.count_bits(foes & 0xf818181f & ~self.c_board.contents.k)

    def count_safe_friends_kings(self):
        if self.c_board.contents.plyr:
            friends = self.c_board.contents.w
        else:
            friends = self.c_board.contents.b
        return state32_lib.count_bits(friends & 0xf818181f & self.c_board.contents.k)

    def count_safe_foes_kings(self):
        if self.c_board.contents.plyr:
            foes = self.c_board.contents.b
        else:
            foes = self.c_board.contents.w
        return state32_lib.count_bits(foes & 0xf818181f & self.c_board.contents.k)

    def count_movable_friends_pawns(self):
        if self.c_board.contents.plyr:
            friends = self.c_board.contents.w
        else:
            friends = self.c_board.contents.b  
        pass   
        

    def count_movable_foes_pawns(self):
        if self.c_board.contents.plyr:
            foes = self.c_board.contents.b
        else:
            foes = self.c_board.contents.w
        pass

    def count_movable_friends_kings(self):
        if self.c_board.contents.plyr:
            friends = self.c_board.contents.w
        else:
            friends = self.c_board.contents.b
        pass

    def count_movable_foes_kings(self):
        if self.c_board.contents.plyr:
            foes = self.c_board.contents.b
        else:
            foes = self.c_board.contents.w
        pass

    def aggregate_distance_promotion_friends(self):
        if self.c_board.contents.plyr:
            friends = self.c_board.contents.w
        else:
            friends = self.c_board.contents.b
        pass

    def aggregate_distance_promotion_foes(self):
        if self.c_board.contents.plyr:
            foes = self.c_board.contents.b
        else:
            foes = self.c_board.contents.w
        pass

    def count_unoccupied_promotion_friends(self):
        if self.c_board.contents.plyr:
            friends = self.c_board.contents.w
            foes = self.c_board.contents.b
            side = white
        else:
            friends = self.c_board.contents.b
            foes = self.c_board.contents.w
            side = black
        if(side == white)
            return state32_lib.count_bits(foes & ~0x0000000f)
        else:
            return state32_lib.count_bits(foes & ~0xf0000000)


    def count_unoccupied_promotion_foes(self):
        if self.c_board.contents.plyr:
            friends = self.c_board.contents.w
            foes = self.c_board.contents.b
            side = black
        else:
            friends = self.c_board.contents.b
            foes = self.c_board.contents.w
            side = white

        if(side == white)
            return state32_lib.count_bits(friends & ~0x0000000f)
        else:
            return state32_lib.count_bits(friends & ~0xf0000000)

    def count_defender_pieces_friends(self):
        if self.c_board.contents.plyr:
            friends = self.c_board.contents.w
        else:
            friends = self.c_board.contents.b
        if self.c_board.contents.plyr:
            return state32_lib.count_bits(friends & 0xff000000)
        else:
            return state32_lib.count_bits(friends & 0x000000ff)

    def count_defender_pieces_foes(self):
        if self.c_board.contents.plyr:
            foes = self.c_board.contents.b
        else:
            foes = self.c_board.contents.w
        if self.c_board.contents.plyr:
            return state32_lib.count_bits(foes & 0x000000ff)
        else:
            return state32_lib.count_bits(foes & 0xff000000)

    def count_attack_pawns_friends(self):
        if self.c_board.contents.plyr:
            friends = self.c_board.contents.w
        else:
            friends = self.c_board.contents.b
        if self.c_board.contents.plyr:
            return state32_lib.count_bits(friends & 0x00000fff)
        else:
            return state32_lib.count_bits(friends & 0xfff00000)

    def count_attack_pawns_foes(self):
        if self.c_board.contents.plyr:
            foes = self.c_board.contents.b
        else:
            foes = self.c_board.contents.w
        if self.c_board.contents.plyr:
            return state32_lib.count_bits(foes & 0xfff00000)
        else:
            return state32_lib.count_bits(foes & 0x00000fff)


    def count_center_pawns_friends(self):
        if self.c_board.contents.plyr:
            friends = self.c_board.contents.w
        else:
            friends = self.c_board.contents.b
        return state32_lib.count_bits(foes & 0x00666600 & ~self.c_board.contents.k)

    def count_center_pawns_foes(self):
        if self.c_board.contents.plyr:
            foes = self.c_board.contents.b
        else:
            foes = self.c_board.contents.w
        return state32_lib.count_bits(foes & 0x00666600 & ~self.c_board.contents.k)

    def count_center_kings_friends(self):
        if self.c_board.contents.plyr:
            friends = self.c_board.contents.w
        else:
            friends = self.c_board.contents.b
        return state32_lib.count_bits(friends & 0x00666600 & self.c_board.contents.k)

    def count_center_kings_foes(self):
        if self.c_board.contents.plyr:
            foes = self.c_board.contents.b
        else:
            foes = self.c_board.contents.w
        return state32_lib.count_bits(foes & 0x00666600 & self.c_board.contents.k)

    def count_diagonalmain_pawns_friends(self):
        if self.c_board.contents.plyr:
            friends = self.c_board.contents.w
        else:
            friends = self.c_board.contents.b
        return state32_lib.count_bits(friends & 0x88442211 & ~self.c_board.contents.k)

    def count_diagonalmain_pawns_foes(self):
        if self.c_board.contents.plyr:
            foes = self.c_board.contents.b
        else:
            foes = self.c_board.contents.w
        return state32_lib.count_bits(foes & 0x88442211 & ~self.c_board.contents.k)


    def count_diagonalmain_kings_friends(self):
        if self.c_board.contents.plyr:
            friends = self.c_board.contents.w
        else:
            friends = self.c_board.contents.b
        return state32_lib.count_bits(friends & 0x88442211 & self.c_board.contents.k)


    def count_diagonalmain_kings_foes(self):
        if self.c_board.contents.plyr:
            foes = self.c_board.contents.b
        else:
            foes = self.c_board.contents.w
        return state32_lib.count_bits(foes & 0x88442211 & self.c_board.contents.k)

    def count_diagonaldouble_pawns_friends(self):
        if self.c_board.contents.plyr:
            friends = self.c_board.contents.w
        else:
            friends = self.c_board.contents.b
        return state32_lib.count_bits(friends & 0x8cc66331 & ~self.c_board.contents.k)


    def count_diagoanldouble_pawns_foes(self):
        if self.c_board.contents.plyr:
            foes = self.c_board.contents.b
        else:
            foes = self.c_board.contents.w
        return state32_lib.count_bits(foes & 0x8cc66331 & ~self.c_board.contents.k)

    def count_diagonaldouble_kings_friends(self):
        if self.c_board.contents.plyr:
            friends = self.c_board.contents.w
        else:
            friends = self.c_board.contents.b
        return state32_lib.count_bits(friends & 0x8cc66331 & self.c_board.contents.k)

    def count_diagonaldouble_kings_foes(self):
        if self.c_board.contents.plyr:
            foes = self.c_board.contents.b
        else:
            foes = self.c_board.contents.w
        return state32_lib.count_bits(foes & 0x8cc66331 & self.c_board.contents.k)


    def count_loner_pawns_friends(self):
        if self.c_board.contents.plyr:
            friends = self.c_board.contents.w
        else:
            friends = self.c_board.contents.b
        pass

    def count_loner_pawns_foes(self):
        if self.c_board.contents.plyr:
            foes = self.c_board.contents.b
        else:
            foes = self.c_board.contents.w
        pass

    def count_loner_kings_friends(self):
        if self.c_board.contents.plyr:
            friends = self.c_board.contents.w
        else:
            friends = self.c_board.contents.b
        pass

    def count_loner_kings_foes(self):
        if self.c_board.contents.plyr:
            foes = self.c_board.contents.b
        else:
            foes = self.c_board.contents.w
        pass

    def count_holes_friends(self):
        if self.c_board.contents.plyr:
            friends = self.c_board.contents.w
        else:
            friends = self.c_board.contents.b
        pass

    def count_holes_foes(self):
        if self.c_board.contents.plyr:
            foes = self.c_board.contents.b
        else:
            foes = self.c_board.contents.w
        pass

    def triangle_friends(self):
        if self.c_board.contents.plyr:
            friends = self.c_board.contents.w
        else:
            friends = self.c_board.contents.b
        if self.c_board.contents.plyr:
            return(state32_lib.count_bits(friends & 0xc4000000) == 3)
        else:
            return(state32_lib.count_bits(friends & 0x00000023) == 3)

    def triangle_foes(self):
        if self.c_board.contents.plyr:
            foes = self.c_board.contents.b
        else:
            foes = self.c_board.contents.w
        if self.c_board.contents.plyr:
            return(state32_lib(foes & 0x00000023) == 3)
        else:
            return(state32_lib(foes & 0xc4000000) == 3)

    def oreo_friends(self):
        if self.c_board.contents.plyr:
            friends = self.c_board.contents.w
        else:
            friends = self.c_board.contents.b
        if self.c_board.contents.plyr:
            return(state32_lib.count_bits(friends & 0x62000000) == 3)
        else:
            return(state32_lib.count_bits(friends & 0x00000046) == 3)

    def oreo_foes(self):
        if self.c_board.contents.plyr:
            foes = self.c_board.contents.b
        else:
            foes = self.c_board.contents.w
        if self.c_board.contents.plyr:
            return(state32_lib(foes & 0x00000046) == 3)
        else:
            return(state32_lib(foes & 0x62000000) == 3)

    def bridge_friends(self):
        if self.c_board.contents.plyr:
            friends = self.c_board.contents.w
        else:
            friends = self.c_board.contents.b
        if self.c_board.contents.plyr:
            return(state32_lib.count_bits(friends & 0xa0000000) == 2)
        else:
            return(state32_lib.count_bits(friends & 0x00000005) == 2)

    def bridge_foes(self):
        if self.c_board.contents.plyr:
            foes = self.c_board.contents.b
        else:
            foes = self.c_board.contents.w
        if self.c_board.contents.plyr:
            return(state32_lib.count_bits(foes & 0x00000005) == 3)
        else:
            return(state32_lib.count_bits(foes & 0xa0000000) == 3)

    def dog_friends(self):
        if self.c_board.contents.plyr:
            friends = self.c_board.contents.w
            foes = self.c_board.contents.b
        else:
            friends = self.c_board.contents.b
            foes = self.c_board.contents.w
        if self.c_board.contents.plyr:
            return((state32_lib.count_bits(friends & 0x80000000) + state32_lib.count_bits(foes & 0x08000000)) == 2)
        else:
            return((state32_lib.count_bits(friends & 0x00000001) + state32_lib.count_bits(foes & 0x00000010)) == 2)

    def dog_foes(self):
        if self.c_board.contents.plyr:
            friends = self.c_board.contents.w
            foes = self.c_board.contents.b
        else:
            friends = self.c_board.contents.b
            foes = self.c_board.contents.w
        if self.c_board.contents.plyr:
            return((state32_lib.count_bits(friends & 0x00000001) + state32_lib.count_bits(foes & 0x00000010)) == 2)
        else:
            return((state32_lib.count_bits(friends & 0x80000000) + state32_lib.count_bits(foes & 0x08000000)) == 2)

    def pawn_corner_friends(self):
        if self.c_board.contents.plyr:
            friends = self.c_board.contents.w
        else:
            friends = self.c_board.contents.b
        pass
    def pawn_corner_foes(self):
        if self.c_board.contents.plyr:
            foes = self.c_board.contents.b
        else:
            foes = self.c_board.contents.w
        pass

    def king_corner_friends(self):
        if self.c_board.contents.plyr:
            friends = self.c_board.contents.w
        else:
            friends = self.c_board.contents.b
        pass

    def king_corner_foes(self):
        if self.c_board.contents.plyr:
            foes = self.c_board.contents.b
        else:
            foes = self.c_board.contents.w
        pass