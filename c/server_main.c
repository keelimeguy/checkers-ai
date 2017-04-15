/*------------------------------------------------------
   Keelin Becker-Wheeler
   CSE4705 - FINAL: Server Protocol Test
------------------------------------------------------*/

#include "mysockets.h"
#include "checkers32.h"

int main(void) {
    int playing_games = 10;
    while (playing_games) {
        Board* board = Board_alloc();
        Board_init(board, 0x00000fff, 0xfff00000, 0x00000000, 0);
        srand(time(NULL));

        printf("%s\n\n", Board_to_string(board));

        if(setup(0, 0, 1)) board = result(board, Move_from_string(send_move(""))); // Play with default
        // if(setup(0, 6, 1)) board = result(board, Move_from_string(send_move(""))); // Play with B as A
        // if(setup(1, 5, 1)) board = result(board, Move_from_string(send_move(""))); // Play with A as B

        int playing_moves = -1, length, index;
        while(board->b && board->w && playing_moves && playing_games) {
            Move** moves;
            length = 0;
            moves = actions(board, &length);
            if (length < 1) break;
            index = (int)(rand()%length);
            board = result(board, moves[index]);

            printf("%s\n", Board_to_string(board));

            char* move = send_move(Move_to_string(moves[index]));
            if (move==0) break;
            if (strstr(move, "Error:")) playing_games = 0;
            else board = result(board, Move_from_string(move));

            if (playing_moves > 0) playing_moves--;
        }

        printf("%s\n", Board_to_string(board));
        end_connection();
        Board_destroy(board);

        if (playing_games > 0) playing_games--;
    }
    return 0;
}
