/*------------------------------------------------------
   Keelin Becker-Wheeler
   CSE4705 - HW4: Checkers Representations
   "32-array" Representation - using 3 unsigned ints
------------------------------------------------------*/

#include "test_keelin.h"

// An unsigned int is 32-bits
// ( Notice that three unsigned ints is equivalent to a 32 length array of 3-bit variables,
//   hence the algorithms in this code will be equivalent to using a 32-bit array )
unsigned int w_board, b_board, k_board; // white, black, and king-ed pieces

int main(void) {
    // Fundamental representation:
    // +b+b+b+b -> -1-2-3-4
    // b+b+b+b+ -> 5-6-7-8-
    // +b+b+b+b -> -9-10-11-12
    // -+-+-+-+ -> 13-14-15-16-
    // +-+-+-+- -> -17-18-19-20
    // w+w+w+w+ -> 21-22-23-24-
    // +w+w+w+w -> -25-26-27-28
    // w+w+w+w+ -> 29-30-31-32-

    // Familiarize yourself with hexadecimal and binary notations..
    // Notice the 32nd through 21st bits are set in w,
    // representing white pieces in their initial positions
    w_board = 0xfff00000; // white pieces
    // Black is set similar to above, 1st to 12th bits set
    b_board = 0x00000fff; // black pieces
    // We do not start with king-ed pieces, so none are set
    k_board = 0x00000000; // king-ed pieces

    print_board(b_board, w_board, k_board);

    char moves[100] = {0};
    white_moves(moves, b_board, w_board, k_board, 0, (unsigned int*){0}, (unsigned int*){0});
    fprintf(stdout, "White Moves: %s\n", moves);

    moves[0] = 0;
    black_moves(moves, b_board, w_board, k_board, 0, (unsigned int*){0}, (unsigned int*){0});
    fprintf(stdout, "Black Moves: %s\n", moves);

    return 0;
}
