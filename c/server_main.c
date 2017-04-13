/*------------------------------------------------------
   Keelin Becker-Wheeler
   CSE4705 - HW4: Checkers Representations
   "32-array" Representation - using 3 unsigned ints
------------------------------------------------------*/

#include "mysockets.h"
#include "checkers32.h"

int main(void) {
    Board* board = Board_alloc();
    Board_init(board, 0x00000fff, 0xfff00000, 0x00000000, 0);

   // printf("%s\n\n", Board_to_string(board));

    if(setup(0)) board = result(board, Move_from_string(send_move("")));

    int playing = -1, length;
    while(board->b && board->w && playing) {
        Move** moves;
        length = 0;
        moves = actions(board, &length);
        // if (length < 1) break;
        board = result(board, moves[0]);

        // printf("%s\n", Board_to_string(board));

        char* move = send_move(Move_to_string(moves[0]));
        if (move==0) break;
        board = result(board, Move_from_string(move));

        if (playing > 0) playing--;
    }

    printf("%s\n", Board_to_string(board));
    end_connection();
    Board_destroy(board);
    return 0;
}
