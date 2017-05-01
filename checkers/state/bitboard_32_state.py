from .state_superclass import CheckersGameState
from checkers.c.structs import *

import warnings
import functools

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

    @functools.total_ordering
    class Move:
        def __init__(self, p_move=None):
            if p_move:
                self.move = state32_lib.Move_copy(p_move)
            if not self.move:
                self.move = state32_lib.Move_alloc()
                state32_lib.Move_init(self.move, 0)

        def __str__(self):
            assert isinstance(self.move, POINTER(MOVE))
            ptr = state32_lib.Move_to_string(self.move)
            string = cast(ptr, c_char_p).value.decode("utf-8")
            state32_lib.free(ptr)
            return string

        def __del__(self):
            state32_lib.Move_destroy(self.move)

        @classmethod
        def from_string(cls, movestr):
            """Convert a move to a string.

            e.g. Move.from_string("(1:3):(3:1)") or whatever
            """
            if not movestr:
                raise ValueError("invalid move string: {}".format(repr(movestr)))
            return cls(state32_lib.Move_from_string(movestr.encode("utf-8")))

        def __eq__(self, other):
            return self.move.contents.length == other.move.contents.length

        def __gt__(self, other):
            return self.move.contents.length > other.move.contents.length

        def __hash__(self):
            assert isinstance(self.move.contents.length, int)
            return sum(self.move.contents.route[i] * 3**i
                       for i in range(self.move.contents.length))

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
        ptr = state32_lib.Board_to_string(self.c_board)
        string = cast(ptr, c_char_p).value.decode("utf-8")
        state32_lib.free(ptr)
        return string

    def __del__(self):
        state32_lib.Board_destroy(self.c_board)

    def __eq__(self, other):
        return (self.c_board.contents.w == other.c_board.contents.w
                and self.c_board.contents.b == other.c_board.contents.b
                and self.c_board.contents.k == other.c_board.contents.k
                and self.c_board.contents.plyr == other.c_board.contents.plyr)

    def __hash__(self):
        # return (((self.c_board.contents.w ^ self.c_board.contents.b)<<32)
        #         | (self.c_board.contents.k ^ self.c_board.contents.plyr))
        return (((self.c_board.contents.w % (self.c_board.contents.b | 3))
                 ^ (self.c_board.contents.b % (self.c_board.contents.w | 3)))
                + self.c_board.contents.k + self.c_board.contents.plyr)

    @classmethod
    def from_string(cls, board_string=FRESH_BOARD_REPR):
        new_board = state32_lib.Board_from_string(create_string_buffer(board_string.encode("utf-8")))
        return cls(0, 0, 0, False, new_board)

    @classmethod
    def move_from_string(cls, movestr=None):
        warnings.warn("Should use {}.Move.from_string instead.".format(cls),
                      category=DeprecationWarning)
        if not movestr:
            return None
        return cls.Move(state32_lib.Move_from_string(movestr.encode("utf-8")))

    def actions(self):
        yield from self.list_actions()

    def list_actions(self):
        movelist = pointer(pointer(MOVE()))
        numMoves = c_int(0)
        movelist = state32_lib.actions(self.c_board, byref(numMoves))
        moves = [Bitboard32State.Move(movelist[i]) for i in range(numMoves.value)]
        state32_lib.Move_list_destroy(movelist, numMoves.value)
        return moves

    def result(self, move):
        if not move:
            raise ValueError("Not a move: {}".format(move))
        new_board = state32_lib.result(self.c_board, move.move)
        return Bitboard32State(0, 0, 0, False, new_board)

    def player(self):
        # Returns player whose turn it is next, not the starting player of a client
        ptr = state32_lib.player(self.c_board)
        string = cast(ptr, c_char_p).value.decode("utf-8")
        state32_lib.free(ptr)
        return string




    # We will use heuristics as described in the Warsaw Paper




    def count_player_and_mask(self, plyr, mask):
        if plyr:
            return state32_lib.count_bits(self.c_board.contents.w & mask)
        return state32_lib.count_bits(self.c_board.contents.b & mask)

    def count_friends(self):
        if self.c_board.contents.plyr:
            friends = self.c_board.contents.w
        else:
            friends = self.c_board.contents.b
        return state32_lib.count_bits(friends)

    def count_friends_pawns(self):
        return self.count_player_and_mask(self.c_board.contents.plyr, ~self.c_board.contents.k)

    def count_friends_kings(self):
        return self.count_player_and_mask(self.c_board.contents.plyr, self.c_board.contents.k)

    def count_foes(self):
        if self.c_board.contents.plyr:
            foes = self.c_board.contents.b
        else:
            foes = self.c_board.contents.w
        return state32_lib.count_bits(foes)

    def count_foes_pawns(self):
        return self.count_player_and_mask(not self.c_board.contents.plyr, ~self.c_board.contents.k)

    def count_foes_kings(self):
        return self.count_player_and_mask(not self.c_board.contents.plyr, self.c_board.contents.k)

    def count_safe_friends_pawns(self):
        return self.count_player_and_mask(self.c_board.contents.plyr, 0xf818181f & ~self.c_board.contents.k)

    def count_safe_foes_pawns(self):
        return self.count_player_and_mask(not self.c_board.contents.plyr, 0xf818181f & ~self.c_board.contents.k)

    def count_safe_friends_kings(self):
        return self.count_player_and_mask(self.c_board.contents.plyr, 0xf818181f & self.c_board.contents.k)

    def count_safe_foes_kings(self):
        return self.count_player_and_mask(not self.c_board.contents.plyr, 0xf818181f & self.c_board.contents.k)


    def count_movable_pawns_check(self, plyr):
        every = self.c_board.contents.w | self.c_board.contents.b
        pos = 1
        count = 0
        if plyr:
            friends = self.c_board.contents.w & ~self.c_board.contents.k
            foes = self.c_board.contents.b
            for i in range(0,32):
                if (friends & pos & 0x0f0f0f00):
                    if (not ((pos>>4)&every) or ((pos&0x07070700) and not ((pos>>3)&every))):
                        count+=1
                    elif ((pos>>4)&foes) and (pos&0xeeeeee00) and not ((pos>>9)&every):
                        count+=1
                    elif ((pos>>3)&foes) and (pos&0x77777700) and not ((pos>>7)&every):
                        count+=1
                elif (friends & pos & 0xf0f0f0f0):
                    if (not ((pos>>4)&every)) or ((pos&0xe0e0e0e0) and not ((pos>>5)&every)):
                        count+=1
                    elif ((pos>>5)&foes) and (pos&0xeeeeee00) and not ((pos>>9)&every):
                        count+=1
                    elif ((pos>>4)&foes) and (pos&0x77777700) and not ((pos>>7)&every):
                        count+=1
                pos = pos<<1
        else:
            friends = self.c_board.contents.b & ~self.c_board.contents.k
            foes = self.c_board.contents.w
            for i in range(0,32):
                if (friends & pos & 0x0f0f0f0f):
                    if (not ((pos<<4)&every)) or ((pos&0x07070707) and not ((pos<<5)&every)):
                        count+=1
                    elif ((pos<<4)&foes) and (pos&0x00eeeeee) and not ((pos<<7)&every):
                        count+=1
                    elif ((pos<<5)&foes) and (pos&0x00777777) and not ((pos<<9)&every):
                        count+=1
                elif (friends & pos & 0x00f0f0f0):
                    if (not ((pos<<4)&every)) or ((pos&0x00e0e0e0) and not ((pos<<3)&every)):
                        count+=1
                    elif ((pos<<3)&foes) and (pos&0x00eeeeee) and not ((pos<<7)&every):
                        count+=1
                    elif ((pos<<4)&foes) and (pos&0x00777777) and not ((pos<<9)&every):
                        count+=1
                pos = pos<<1
        return count

    def count_movable_friends_pawns(self):
        return self.count_movable_pawns_check(self.c_board.contents.plyr)

    def count_movable_foes_pawns(self):
        return self.count_movable_pawns_check(not self.c_board.contents.plyr)


    def count_movable_kings_check(self, plyr):
        every = self.c_board.contents.w | self.c_board.contents.b
        pos = 1
        count = 0
        if plyr:
            friends = self.c_board.contents.w & self.c_board.contents.k
            foes = self.c_board.contents.b
        else:
            friends = self.c_board.contents.b & self.c_board.contents.k
            foes = self.c_board.contents.w
        for i in range(0,32):
            if (friends & pos & 0x0f0f0f0f):
                if (not ((pos<<4)&every)) or ((pos&0x07070707) and not ((pos<<5)&every)):
                    count+=1
                elif ((pos<<4)&foes) and (pos&0x00eeeeee) and not ((pos<<7)&every):
                    count+=1
                elif ((pos<<5)&foes) and (pos&0x00777777) and not ((pos<<9)&every):
                    count+=1
                elif (friends & pos & 0x0f0f0f00):
                    if (not ((pos>>4)&every) or ((pos&0x07070700) and not ((pos>>3)&every))):
                        count+=1
                    elif ((pos>>4)&foes) and (pos&0xeeeeee00) and not ((pos>>9)&every):
                        count+=1
                    elif ((pos>>3)&foes) and (pos&0x77777700) and not ((pos>>7)&every):
                        count+=1
            elif (friends & pos & 0xf0f0f0f0):
                if (not ((pos>>4)&every)) or ((pos&0xe0e0e0e0) and not ((pos>>5)&every)):
                    count+=1
                elif ((pos>>5)&foes) and (pos&0xeeeeee00) and not ((pos>>9)&every):
                    count+=1
                elif ((pos>>4)&foes) and (pos&0x77777700) and not ((pos>>7)&every):
                    count+=1
                elif (friends & pos & 0x00f0f0f0):
                    if (not ((pos<<4)&every)) or ((pos&0x00e0e0e0) and not ((pos<<3)&every)):
                        count+=1
                    elif ((pos<<3)&foes) and (pos&0x00eeeeee) and not ((pos<<7)&every):
                        count+=1
                    elif ((pos<<4)&foes) and (pos&0x00777777) and not ((pos<<9)&every):
                        count+=1
            pos = pos<<1
        return count

    def count_movable_friends_kings(self):
        return self.count_movable_kings_check(self.c_board.contents.plyr)

    def count_movable_foes_kings(self):
        return self.count_movable_kings_check(not self.c_board.contents.plyr)


    def aggregate_distance_check(self, plyr):
        pos = 1
        dist = 0
        if plyr:
            friends = self.c_board.contents.w & ~self.c_board.contents.k
            for i in range(1,33):
                if friends & pos:
                    dist += 7 - state32_lib.pos_to_row(i)
                pos = pos<<1
        else:
            friends = self.c_board.contents.b & ~self.c_board.contents.k
            for i in range(1,33):
                if friends & pos:
                    dist += state32_lib.pos_to_row(i)
                pos = pos<<1
        return dist

    def aggregate_distance_promotion_friends(self):
        return self.aggregate_distance_check(self.c_board.contents.plyr)

    def aggregate_distance_promotion_foes(self):
        return self.aggregate_distance_check(not self.c_board.contents.plyr)


    def count_unoccupied_promotion_friends(self):
        every = self.c_board.contents.b|self.c_board.contents.w
        if self.c_board.contents.plyr:
            return 4 - state32_lib.count_bits(every & 0x0000000f)
        else:
            return 4 - state32_lib.count_bits(every & 0xf0000000)

    def count_unoccupied_promotion_foes(self):
        every = self.c_board.contents.b|self.c_board.contents.w
        if self.c_board.contents.plyr:
            return 4 - state32_lib.count_bits(every & 0xf0000000)
        else:
            return 4 - state32_lib.count_bits(every & 0x0000000f)

    def count_defender_pieces_friends(self):
        if self.c_board.contents.plyr:
            friends = self.c_board.contents.w
            return state32_lib.count_bits(friends & 0xff000000)
        else:
            friends = self.c_board.contents.b
            return state32_lib.count_bits(friends & 0x000000ff)

    def count_defender_pieces_foes(self):
        if self.c_board.contents.plyr:
            foes = self.c_board.contents.b
            return state32_lib.count_bits(foes & 0x000000ff)
        else:
            foes = self.c_board.contents.w
            return state32_lib.count_bits(foes & 0xff000000)

    def count_attack_pawns_friends(self):
        if self.c_board.contents.plyr:
            friends = self.c_board.contents.w&~self.c_board.contents.k
            return state32_lib.count_bits(friends & 0x00000fff)
        else:
            friends = self.c_board.contents.b&~self.c_board.contents.k
            return state32_lib.count_bits(friends & 0xfff00000)

    def count_attack_pawns_foes(self):
        if self.c_board.contents.plyr:
            foes = self.c_board.contents.b&~self.c_board.contents.k
            return state32_lib.count_bits(foes & 0xfff00000)
        else:
            foes = self.c_board.contents.w&~self.c_board.contents.k
            return state32_lib.count_bits(foes & 0x00000fff)

    def count_center_pawns_friends(self):
        return self.count_player_and_mask(self.c_board.contents.plyr, 0x00666600 & ~self.c_board.contents.k)

    def count_center_pawns_foes(self):
        return self.count_player_and_mask(not self.c_board.contents.plyr, 0x00666600 & ~self.c_board.contents.k)

    def count_center_kings_friends(self):
        return self.count_player_and_mask(self.c_board.contents.plyr, 0x00666600 & self.c_board.contents.k)

    def count_center_kings_foes(self):
        return self.count_player_and_mask(not self.c_board.contents.plyr, 0x00666600 & self.c_board.contents.k)

    def count_diagonalmain_pawns_friends(self):
        return self.count_player_and_mask(self.c_board.contents.plyr, 0x11224488 & ~self.c_board.contents.k)

    def count_diagonalmain_pawns_foes(self):
        return self.count_player_and_mask(not self.c_board.contents.plyr, 0x11224488 & ~self.c_board.contents.k)

    def count_diagonalmain_kings_friends(self):
        return self.count_player_and_mask(self.c_board.contents.plyr, 0x11224488 & self.c_board.contents.k)

    def count_diagonalmain_kings_foes(self):
        return self.count_player_and_mask(not self.c_board.contents.plyr, 0x11224488 & self.c_board.contents.k)

    def count_diagonaldouble_pawns_friends(self):
        return self.count_player_and_mask(self.c_board.contents.plyr, 0x8cc66331 & ~self.c_board.contents.k)

    def count_diagonaldouble_pawns_foes(self):
        return self.count_player_and_mask(not self.c_board.contents.plyr, 0x8cc66331 & ~self.c_board.contents.k)

    def count_diagonaldouble_kings_friends(self):
        return self.count_player_and_mask(self.c_board.contents.plyr, 0x8cc66331 & self.c_board.contents.k)

    def count_diagonaldouble_kings_foes(self):
        return self.count_player_and_mask(not self.c_board.contents.plyr, 0x8cc66331 & self.c_board.contents.k)


    def count_loner(self, mask):
        empty = ~(self.c_board.contents.b|self.c_board.contents.w)
        pos = 1
        num_loner = 0
        for i in range(1,33):
            count = 0
            if pos&mask&0x07e7e7e0:
                if pos&0x0f0f0f0f:
                    count = len([p for p in [pos>>4, pos>>3, pos<<4, pos<<5] if p&empty])
                else:
                    count = len([p for p in [pos>>5, pos>>4, pos<<3, pos<<4] if p&empty])
                if count==4:
                    num_loner+=1
            pos = pos << 1
        return num_loner

    def count_loner_pawns_friends(self):
        if self.c_board.contents.plyr:
            return self.count_loner(self.c_board.contents.w&~self.c_board.contents.k)
        return self.count_loner(self.c_board.contents.b&~self.c_board.contents.k)

    def count_loner_pawns_foes(self):
        if self.c_board.contents.plyr:
            return self.count_loner(self.c_board.contents.b&~self.c_board.contents.k)
        return self.count_loner(self.c_board.contents.w&~self.c_board.contents.k)

    def count_loner_kings_friends(self):
        if self.c_board.contents.plyr:
            return self.count_loner(self.c_board.contents.w&self.c_board.contents.k)
        return self.count_loner(self.c_board.contents.b&self.c_board.contents.k)

    def count_loner_kings_foes(self):
        if self.c_board.contents.plyr:
            return self.count_loner(self.c_board.contents.b&self.c_board.contents.k)
        return self.count_loner(self.c_board.contents.w&self.c_board.contents.k)


    # hole: empty squares adjacent to at least three pieces of the same color.
    def count_holes(self, plyr):
        empty = ~(self.c_board.contents.b|self.c_board.contents.w)
        if plyr:
            mask = self.c_board.contents.w
        else:
            mask = self.c_board.contents.b
        pos = 1
        num_holes = 0
        for i in range(1,33):
            count = 0
            if pos&empty&0x07e7e7e0:
                if pos&0x0f0f0f0f:
                    count = len([p for p in [pos>>4, pos>>3, pos<<4, pos<<5] if p&mask])
                else:
                    count = len([p for p in [pos>>5, pos>>4, pos<<3, pos<<4] if p&mask])
                if count>=3:
                    num_holes+=1
            pos = pos << 1
        return num_holes

    def count_holes_friends(self):
        return self.count_holes(self.c_board.contents.plyr)

    def count_holes_foes(self):
        return self.count_holes(not self.c_board.contents.plyr)


    def triangle_check(self, plyr):
        if plyr:
            return(1 if (self.c_board.contents.w & 0xc4000000 == 0xc4000000) else 0)
        return(1 if (self.c_board.contents.b & 0x00000023 == 0x00000023) else 0)

    def triangle_friends(self):
        return self.triangle_check(self.c_board.contents.plyr)

    def triangle_foes(self):
        return self.triangle_check(not self.c_board.contents.plyr)


    def oreo_check(self, plyr):
        if plyr:
            return(1 if (self.c_board.contents.w & 0x62000000 == 0x62000000) else 0)
        return(1 if (self.c_board.contents.b & 0x00000046 == 0x00000046) else 0)

    def oreo_friends(self):
        return self.oreo_check(self.c_board.contents.plyr)

    def oreo_foes(self):
        return self.oreo_check(not self.c_board.contents.plyr)


    def bridge_check(self, plyr):
        if plyr:
            return(1 if (self.c_board.contents.w & 0xa0000000 == 0xa0000000) else 0)
        return(1 if (self.c_board.contents.b & 0x00000005 == 0x00000005) else 0)

    def bridge_friends(self):
        return self.bridge_check(self.c_board.contents.plyr)

    def bridge_foes(self):
        return self.bridge_check(not self.c_board.contents.plyr)


    def dog_check(self, plyr):
        if plyr:
            return(1 if (self.c_board.contents.w & 0x80000000 and self.c_board.contents.b & 0x08000000) else 0)
        return(1 if (self.c_board.contents.w & 0x00000010 and self.c_board.contents.b & 0x00000001) else 0)

    def dog_friends(self):
        return self.dog_check(self.c_board.contents.plyr)

    def dog_foes(self):
        return self.dog_check(not self.c_board.contents.plyr)


    def corner_check(self, plyr, king):
        if plyr:
            if king:
                mask = self.c_board.contents.b & self.c_board.contents.k
            else:
                mask = self.c_board.contents.w & ~self.c_board.contents.k
            return state32_lib.count_bits(mask & 0x10000000)
        if king:
            mask = self.c_board.contents.w & self.c_board.contents.k
        else:
            mask = self.c_board.contents.b & ~self.c_board.contents.k
        return state32_lib.count_bits(mask & 0x00000008)

    def pawn_corner_friends(self):
        return self.corner_check(self.c_board.contents.plyr, False)

    def pawn_corner_foes(self):
        return self.corner_check(not self.c_board.contents.plyr, False)

    def king_corner_friends(self):
        return self.corner_check(not self.c_board.contents.plyr, True)

    def king_corner_foes(self):
        return self.corner_check(self.c_board.contents.plyr, True)
