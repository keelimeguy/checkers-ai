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
            if p_move:
                self.move = state32_lib.Move_copy(p_move)
            if not self.move:
                self.move = state32_lib.Move_alloc()
                state32_lib.Move_init(self.move, 0)

        def __str__(self):
            ptr = state32_lib.Move_to_string(self.move)
            string = cast(ptr, c_char_p).value.decode("utf-8")
            state32_lib.free(ptr)
            return string

        def destroy(self):
            state32_lib.Move_destroy(self.move)

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

    def destroy(self):
        state32_lib.Board_destroy(self.c_board)

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
        state32_lib.Move_list_destroy(movelist, numMoves.value)
        return moves

    def result(self, move=None):
        if not move:
            return self
        new_board = state32_lib.result(self.c_board, move.move)
        return Bitboard32State(0, 0, 0, False, new_board)

    def player(self):
        ptr = state32_lib.player(self.c_board)
        string = cast(ptr, c_char_p).value.decode("utf-8")
        state32_lib.free(ptr)
        return string

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
        every = self.c_board.contents.w | self.c_board.contents.b
        pos = 1
        count = 0
        if self.c_board.contents.plyr:
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

    def count_movable_foes_pawns(self):
        every = self.c_board.contents.w | self.c_board.contents.b
        pos = 1
        count = 0
        if self.c_board.contents.plyr:
            foes = self.c_board.contents.b & ~self.c_board.contents.k
            friends = self.c_board.contents.w
            for i in range(0,32):
                if (foes & pos & 0x0f0f0f0f):
                    if (not ((pos<<4)&every)) or ((pos&0x07070707) and not ((pos<<5)&every)):
                        count+=1
                    elif ((pos<<4)&friends) and (pos&0x00eeeeee) and not ((pos<<7)&every):
                        count+=1
                    elif ((pos<<5)&friends) and (pos&0x00777777) and not ((pos<<9)&every):
                        count+=1
                elif (foes & pos & 0x00f0f0f0):
                    if (not ((pos<<4)&every)) or ((pos&0x00e0e0e0) and not ((pos<<3)&every)):
                        count+=1
                    elif ((pos<<3)&friends) and (pos&0x00eeeeee) and not ((pos<<7)&every):
                        count+=1
                    elif ((pos<<4)&friends) and (pos&0x00777777) and not ((pos<<9)&every):
                        count+=1
                pos = pos<<1
        else:
            foes = self.c_board.contents.w & ~self.c_board.contents.k
            friends = self.c_board.contents.b
            for i in range(0,32):
                if (foes & pos & 0x0f0f0f00):
                    if (not ((pos>>4)&every)) or ((pos&0x07070700) and not ((pos>>3)&every)):
                        count+=1
                    elif ((pos>>4)&friends) and (pos&0xeeeeee00) and not ((pos>>9)&every):
                        count+=1
                    elif ((pos>>3)&friends) and (pos&0x77777700) and not ((pos>>7)&every):
                        count+=1
                elif (foes & pos & 0xf0f0f0f0):
                    if (not ((pos>>4)&every)) or ((pos&0xe0e0e0e0) and not ((pos>>5)&every)):
                        count+=1
                    elif ((pos>>5)&friends) and (pos&0xeeeeee00) and not ((pos>>9)&every):
                        count+=1
                    elif ((pos>>4)&friends) and (pos&0x77777700) and not ((pos>>7)&every):
                        count+=1
                pos = pos<<1
        return count

    def count_movable_friends_kings(self):
        every = self.c_board.contents.w | self.c_board.contents.b
        pos = 1
        count = 0
        if self.c_board.contents.plyr:
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

    def count_movable_foes_kings(self):
        every = self.c_board.contents.w | self.c_board.contents.b
        pos = 1
        count = 0
        if self.c_board.contents.plyr:
            foes = self.c_board.contents.b & self.c_board.contents.k
            friends = self.c_board.contents.w
        else:
            foes = self.c_board.contents.w & self.c_board.contents.k
            friends = self.c_board.contents.b
        for i in range(0,32):
            if (foes & pos & 0x0f0f0f0f):
                if (not ((pos<<4)&every)) or ((pos&0x07070707) and not ((pos<<5)&every)):
                    count+=1
                elif ((pos<<4)&friends) and (pos&0x00eeeeee) and not ((pos<<7)&every):
                    count+=1
                elif ((pos<<5)&friends) and (pos&0x00777777) and not ((pos<<9)&every):
                    count+=1
                elif (foes & pos & 0x0f0f0f00):
                    if ((not ((pos>>4)&every)) or ((pos&0x07070700) and not ((pos>>3)&every))):
                        count+=1
                    elif ((pos>>4)&friends) and (pos&0xeeeeee00) and not ((pos>>9)&every):
                        count+=1
                    elif ((pos>>3)&friends) and (pos&0x77777700) and not ((pos>>7)&every):
                        count+=1
            elif (foes & pos & 0xf0f0f0f0):
                if (not ((pos>>4)&every)) or ((pos&0xe0e0e0e0) and not ((pos>>5)&every)):
                    count+=1
                elif ((pos>>5)&friends) and (pos&0xeeeeee00) and not ((pos>>9)&every):
                    count+=1
                elif ((pos>>4)&friends) and (pos&0x77777700) and not ((pos>>7)&every):
                    count+=1
                elif (foes & pos & 0x00f0f0f0):
                    if (not ((pos<<4)&every)) or ((pos&0x00e0e0e0) and not ((pos<<3)&every)):
                        count+=1
                    elif ((pos<<3)&friends) and (pos&0x00eeeeee) and not ((pos<<7)&every):
                        count+=1
                    elif ((pos<<4)&friends) and (pos&0x00777777) and not ((pos<<9)&every):
                        count+=1
            pos = pos<<1
        return count

    def aggregate_distance_promotion_friends(self):
        pos = 1
        dist = 0
        if self.c_board.contents.plyr:
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

    def aggregate_distance_promotion_foes(self):
        pos = 1
        dist = 0
        if self.c_board.contents.plyr:
            foes = self.c_board.contents.b & ~self.c_board.contents.k
            for i in range(1,33):
                if foes & pos:
                    dist += state32_lib.pos_to_row(i)
                pos = pos<<1
        else:
            foes = self.c_board.contents.w & ~self.c_board.contents.k
            for i in range(1,33):
                if foes & pos:
                    dist += 7 - state32_lib.pos_to_row(i)
                pos = pos<<1
        return dist

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
        if self.c_board.contents.plyr:
            friends = self.c_board.contents.w
        else:
            friends = self.c_board.contents.b
        return state32_lib.count_bits(friends & 0x00666600 & ~self.c_board.contents.k)

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
        return state32_lib.count_bits(friends & 0x11224488 & ~self.c_board.contents.k)

    def count_diagonalmain_pawns_foes(self):
        if self.c_board.contents.plyr:
            foes = self.c_board.contents.b
        else:
            foes = self.c_board.contents.w
        return state32_lib.count_bits(foes & 0x11224488 & ~self.c_board.contents.k)


    def count_diagonalmain_kings_friends(self):
        if self.c_board.contents.plyr:
            friends = self.c_board.contents.w
        else:
            friends = self.c_board.contents.b
        return state32_lib.count_bits(friends & 0x11224488 & self.c_board.contents.k)


    def count_diagonalmain_kings_foes(self):
        if self.c_board.contents.plyr:
            foes = self.c_board.contents.b
        else:
            foes = self.c_board.contents.w
        return state32_lib.count_bits(foes & 0x11224488 & self.c_board.contents.k)

    def count_diagonaldouble_pawns_friends(self):
        if self.c_board.contents.plyr:
            friends = self.c_board.contents.w
        else:
            friends = self.c_board.contents.b
        return state32_lib.count_bits(friends & 0x8cc66331 & ~self.c_board.contents.k)

    def count_diagonaldouble_pawns_foes(self):
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
        empty = ~(self.c_board.contents.b|self.c_board.contents.w)
        if self.c_board.contents.plyr:
            friends = self.c_board.contents.w&~self.c_board.contents.k
        else:
            friends = self.c_board.contents.b&~self.c_board.contents.k
        pos = 1
        num_loner = 0
        for i in range(1,33):
            count = 0
            if pos&friends&0x07e7e7e0:
                if pos&0x0f0f0f0f:
                    count = len([p for p in [pos>>4, pos>>3, pos<<4, pos<<5] if p&empty])
                else:
                    count = len([p for p in [pos>>5, pos>>4, pos<<3, pos<<4] if p&empty])
                if count==4:
                    num_loner+=1
            pos = pos << 1
        return num_loner

    def count_loner_pawns_foes(self):
        empty = ~(self.c_board.contents.b|self.c_board.contents.w)
        if self.c_board.contents.plyr:
            foes = self.c_board.contents.b&~self.c_board.contents.k
        else:
            foes = self.c_board.contents.w&~self.c_board.contents.k
        pos = 1
        num_loner = 0
        for i in range(1,33):
            count = 0
            if pos&foes&0x07e7e7e0:
                if pos&0x0f0f0f0f:
                    count = len([p for p in [pos>>4, pos>>3, pos<<4, pos<<5] if p&empty])
                else:
                    count = len([p for p in [pos>>5, pos>>4, pos<<3, pos<<4] if p&empty])
                if count==4:
                    num_loner+=1
            pos = pos << 1
        return num_loner

    def count_loner_kings_friends(self):
        empty = ~(self.c_board.contents.b|self.c_board.contents.w)
        if self.c_board.contents.plyr:
            friends = self.c_board.contents.w&self.c_board.contents.k
        else:
            friends = self.c_board.contents.b&self.c_board.contents.k
        pos = 1
        num_loner = 0
        for i in range(1,33):
            count = 0
            if pos&friends&0x07e7e7e0:
                if pos&0x0f0f0f0f:
                    count = len([p for p in [pos>>4, pos>>3, pos<<4, pos<<5] if p&empty])
                else:
                    count = len([p for p in [pos>>5, pos>>4, pos<<3, pos<<4] if p&empty])
                if count==4:
                    num_loner+=1
            pos = pos << 1
        return num_loner

    def count_loner_kings_foes(self):
        empty = ~(self.c_board.contents.b|self.c_board.contents.w)
        if self.c_board.contents.plyr:
            foes = self.c_board.contents.b&self.c_board.contents.k
        else:
            foes = self.c_board.contents.w&self.c_board.contents.k
        pos = 1
        num_loner = 0
        for i in range(1,33):
            count = 0
            if pos&foes&0x07e7e7e0:
                if pos&0x0f0f0f0f:
                    count = len([p for p in [pos>>4, pos>>3, pos<<4, pos<<5] if p&empty])
                else:
                    count = len([p for p in [pos>>5, pos>>4, pos<<3, pos<<4] if p&empty])
                if count==4:
                    num_loner+=1
            pos = pos << 1
        return num_loner

    # hole: empty squares adjacent to at least three pieces of the same color.

    def count_holes_friends(self):
        empty = ~(self.c_board.contents.b|self.c_board.contents.w)
        if self.c_board.contents.plyr:
            friends = self.c_board.contents.w
        else:
            friends = self.c_board.contents.b
        pos = 1
        num_holes = 0
        for i in range(1,33):
            count = 0
            if pos&empty&0x07e7e7e0:
                if pos&0x0f0f0f0f:
                    count = len([p for p in [pos>>4, pos>>3, pos<<4, pos<<5] if p&friends])
                else:
                    count = len([p for p in [pos>>5, pos>>4, pos<<3, pos<<4] if p&friends])
                if count>=3:
                    num_holes+=1
            pos = pos << 1
        return num_holes

    def count_holes_foes(self):
        empty = ~(self.c_board.contents.b|self.c_board.contents.w)
        if self.c_board.contents.plyr:
            foes = self.c_board.contents.b
        else:
            foes = self.c_board.contents.w
        pos = 1
        num_holes = 0
        for i in range(1,33):
            count = 0
            if pos&empty&0x07e7e7e0:
                if pos&0x0f0f0f0f:
                    count = len([p for p in [pos>>4, pos>>3, pos<<4, pos<<5] if p&foes])
                else:
                    count = len([p for p in [pos>>5, pos>>4, pos<<3, pos<<4] if p&foes])
                if count>=3:
                    num_holes+=1
            pos = pos << 1
        return num_holes

    def triangle_friends(self):
        if self.c_board.contents.plyr:
            friends = self.c_board.contents.w
            return(state32_lib.count_bits(friends & 0xc4000000) == 3)
        else:
            friends = self.c_board.contents.b
            return(state32_lib.count_bits(friends & 0x00000023) == 3)

    def triangle_foes(self):
        if self.c_board.contents.plyr:
            foes = self.c_board.contents.b
            return(state32_lib.count_bits(foes & 0x00000023) == 3)
        else:
            foes = self.c_board.contents.w
            return(state32_lib.count_bits(foes & 0xc4000000) == 3)

    def oreo_friends(self):
        if self.c_board.contents.plyr:
            friends = self.c_board.contents.w
            return(state32_lib.count_bits(friends & 0x62000000) == 3)
        else:
            friends = self.c_board.contents.b
            return(state32_lib.count_bits(friends & 0x00000046) == 3)

    def oreo_foes(self):
        if self.c_board.contents.plyr:
            foes = self.c_board.contents.b
            return(state32_lib.count_bits(foes & 0x00000046) == 3)
        else:
            foes = self.c_board.contents.w
            return(state32_lib.count_bits(foes & 0x62000000) == 3)

    def bridge_friends(self):
        if self.c_board.contents.plyr:
            friends = self.c_board.contents.w
            return(state32_lib.count_bits(friends & 0xa0000000) == 2)
        else:
            friends = self.c_board.contents.b
            return(state32_lib.count_bits(friends & 0x00000005) == 2)

    def bridge_foes(self):
        if self.c_board.contents.plyr:
            foes = self.c_board.contents.b
            return(state32_lib.count_bits(foes & 0x00000005) == 2)
        else:
            foes = self.c_board.contents.w
            return(state32_lib.count_bits(foes & 0xa0000000) == 2)

    def dog_friends(self):
        if self.c_board.contents.plyr:
            friends = self.c_board.contents.w
            foes = self.c_board.contents.b
            return((state32_lib.count_bits(friends & 0x80000000) + state32_lib.count_bits(foes & 0x08000000)) == 2)
        else:
            friends = self.c_board.contents.b
            foes = self.c_board.contents.w
            return((state32_lib.count_bits(friends & 0x00000001) + state32_lib.count_bits(foes & 0x00000010)) == 2)

    def dog_foes(self):
        if self.c_board.contents.plyr:
            friends = self.c_board.contents.w
            foes = self.c_board.contents.b
            return((state32_lib.count_bits(friends & 0x00000010) + state32_lib.count_bits(foes & 0x00000001)) == 2)
        else:
            friends = self.c_board.contents.b
            foes = self.c_board.contents.w
            return((state32_lib.count_bits(friends & 0x08000000) + state32_lib.count_bits(foes & 0x80000000)) == 2)

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
