/*------------------------------------------------------
   Keelin Becker-Wheeler
   CSE4705 - HW4: Checkers Representations
   "32-array" Representation - using 3 unsigned ints
------------------------------------------------------*/

#include "checkers32.h"

int main(void) {
    Board* board = Board_alloc();
    board->b = 0x00e06021;
    board->w = 0x00000200;
    board->k = 0x00000200;
    board->plyr = 1;

    fprintf(stdout, "%s\n", Board_to_string(board));

    Move** moves;
    for (int i = 0; i < 2; i++) {
        printf("%d pieces total\n", count_bits(board->b|board->w));
        printf("%d black pieces\n", count_bits(board->b));
        printf("%d white pieces\n", count_bits(board->w));

        int length = 0;
        moves = actions(board, &length);
        board = result(board, moves[0]);
        fprintf(stdout, "Making first available move...\n\n");

        fprintf(stdout, "%s\n", Board_to_string(board));
    }

    printf("%d pieces total\n", count_bits(board->b|board->w));
    printf("%d black pieces\n", count_bits(board->b));
    printf("%d white pieces\n", count_bits(board->w));

    Board_destroy(board);
    return 0;
}
