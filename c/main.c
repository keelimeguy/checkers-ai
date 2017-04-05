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
unsigned int curPlayer;

void setup(unsigned int b, unsigned int w, unsigned int k, unsigned short plyr);
void printState(void);
void player(char* str);
void actions(char* moves);
void result(char* move);

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
    curPlayer = 0; // 0 for player black, 1 for player white

    char moves[999] = {0};
    char playerStr[5] = {0};

    printState();

    player(playerStr);
    actions(moves);

    fprintf(stdout, "Player: %s\n", playerStr);
    fprintf(stdout, "Actions: %s\n", moves);

    fprintf(stdout, "\n");

    result("(5:1):(4:0)");

    fprintf(stdout, "\n");

    moves[0] = 0;

    printState();

    player(playerStr);
    actions(moves);

    fprintf(stdout, "Player: %s\n", playerStr);
    fprintf(stdout, "Actions: %s\n", moves);

    fprintf(stdout, "\n");

    result("(2:2):(3:1)");

    fprintf(stdout, "\n");

    moves[0] = 0;

    printState();

    player(playerStr);
    actions(moves);

    fprintf(stdout, "Player: %s\n", playerStr);
    fprintf(stdout, "Actions: %s\n", moves);

    fprintf(stdout, "\n");

    result("(4:0):(2:2)");

    fprintf(stdout, "\n");

    moves[0] = 0;

    printState();

    player(playerStr);
    actions(moves);

    fprintf(stdout, "Player: %s\n", playerStr);
    fprintf(stdout, "Actions: %s\n", moves);

//--------------------------------------------
    moves[0] = 0;

    fprintf(stdout, "\n");

    setup(0x00e06021, 0x00000200, 0x00000200, 1);

    printState();

    player(playerStr);
    actions(moves);

    fprintf(stdout, "Player: %s\n", playerStr);
    fprintf(stdout, "Actions: %s\n", moves);


    return 0;
}

void setup(unsigned int b, unsigned int w, unsigned int k, unsigned short plyr) {
    b_board = b;
    w_board = w;
    k_board = k;
    curPlayer = plyr;
}

void printState(void) {
    print_board(b_board, w_board, k_board);
}

void player(char* str) {
    if (curPlayer)
        sprintf(str, "White");
    else
        sprintf(str, "Black");
}

void actions(char* moves) {
    if (curPlayer)
        white_moves(moves, b_board, w_board, k_board, 0, (unsigned int*){0}, (unsigned int*){0});
    else
        black_moves(moves, b_board, w_board, k_board, 0, (unsigned int*){0}, (unsigned int*){0});
}

void result(char* move) {
    unsigned int len = strlen(move);
    if (move==0 || len<11) return;
    unsigned short row_start = (unsigned short)(move[1]-48); // 48 is ASCII for '0'
    unsigned short col_start = (unsigned short)(move[3]-48);
    unsigned short row_end = row_start;
    unsigned short col_end = col_start;

    unsigned int index = 7;
    while(index < len) {
        row_start = row_end;
        col_start = col_end;

        row_end = (unsigned short)(move[index]-48);
        col_end = (unsigned short)(move[index+2]-48);

        unsigned short pos_start = (7-row_start)*4+1 + col_start/2;
        unsigned short pos_end = (7-row_end)*4+1 + col_end/2;
        fprintf(stdout, "(%d:%d):(%d:%d) -> ", row_start, col_start, row_end, col_end);
        fprintf(stdout, "(%d):(%d)\n", pos_start, pos_end);

        if(curPlayer) {
            w_board&=~(1<<(pos_start-1));
            if (pos_start-pos_end>6 || pos_start-pos_end<6) { // Jumped a piece
                if (pos_start-pos_end == -7) {
                    if (row_start%2==0) { // If started on even row
                        b_board&=~(1<<(pos_start+2)); // +3 (-1)
                        k_board&=~(1<<(pos_start+2)); // +3 (-1)
                    } else {     // If started on odd row
                        b_board&=~(1<<(pos_start+3)); // +4 (-1)
                        k_board&=~(1<<(pos_start+3)); // +4 (-1)
                    }
                } else if (pos_start-pos_end == -9) {
                    if (row_start%2==0) { // If started on even row
                        b_board&=~(1<<(pos_start+3)); // +4 (-1)
                        k_board&=~(1<<(pos_start+3)); // +4 (-1)
                    } else {     // If started on odd row
                        b_board&=~(1<<(pos_start+4)); // +5 (-1)
                        k_board&=~(1<<(pos_start+4)); // +5 (-1)
                    }
                } else if (pos_start-pos_end == 7) {
                    if (row_start%2==0) { // If started on even row
                        b_board&=~(1<<(pos_start-5)); // -4 (-1)
                        k_board&=~(1<<(pos_start-5)); // -4 (-1)
                    } else {     // If started on odd row
                        b_board&=~(1<<(pos_start-4)); // -3 (-1)
                        k_board&=~(1<<(pos_start-4)); // -3 (-1)
                    }
                } else if (pos_start-pos_end == 9) {
                    if (row_start%2==0) { // If started on even row
                        b_board&=~(1<<(pos_start-6)); // -5 (-1)
                        k_board&=~(1<<(pos_start-6)); // -5 (-1)
                    } else {     // If started on odd row
                        b_board&=~(1<<(pos_start-5)); // -4 (-1)
                        k_board&=~(1<<(pos_start-5)); // -4 (-1)
                    }
                }
            }
            w_board|=(1<<(pos_end-1));
            if(k_board&(1<<(pos_start-1))) {
                k_board&=~(1<<(pos_start-1));
                k_board|=(1<<(pos_end-1));
            }
        } else {
            b_board&=~(1<<(pos_start-1));
            if (pos_start-pos_end>6 || pos_start-pos_end<6) { // Jumped a piece
                if (pos_start-pos_end == -7) {
                    if (row_start%2==0) { // If started on even row
                        w_board&=~(1<<(pos_start+2)); // +3 (-1)
                        k_board&=~(1<<(pos_start+2)); // +3 (-1)
                    } else {     // If started on odd row
                        w_board&=~(1<<(pos_start+3)); // +4 (-1)
                        k_board&=~(1<<(pos_start+3)); // +4 (-1)
                    }
                } else if (pos_start-pos_end == -9) {
                    if (row_start%2==0) { // If started on even row
                        w_board&=~(1<<(pos_start+3)); // +4 (-1)
                        k_board&=~(1<<(pos_start+3)); // +4 (-1)
                    } else {     // If started on odd row
                        w_board&=~(1<<(pos_start+4)); // +5 (-1)
                        k_board&=~(1<<(pos_start+4)); // +5 (-1)
                    }
                } else if (pos_start-pos_end == 7) {
                    if (row_start%2==0) { // If started on even row
                        w_board&=~(1<<(pos_start-5)); // -4 (-1)
                        k_board&=~(1<<(pos_start-5)); // -4 (-1)
                    } else {     // If started on odd row
                        w_board&=~(1<<(pos_start-4)); // -3 (-1)
                        k_board&=~(1<<(pos_start-4)); // -3 (-1)
                    }
                } else if (pos_start-pos_end == 9) {
                    if (row_start%2==0) { // If started on even row
                        w_board&=~(1<<(pos_start-6)); // -5 (-1)
                        k_board&=~(1<<(pos_start-6)); // -5 (-1)
                    } else {     // If started on odd row
                        w_board&=~(1<<(pos_start-5)); // -4 (-1)
                        k_board&=~(1<<(pos_start-5)); // -4 (-1)
                    }
                }
            }
            b_board|=(1<<(pos_end-1));
            if(k_board&(1<<(pos_start-1))) {
                k_board&=~(1<<(pos_start-1));
                k_board|=(1<<(pos_end-1));
            }
        }
        index+=6;
    }
    curPlayer = (curPlayer+1)%2;
}