/*------------------------------------------------------
   Keelin Becker-Wheeler
   CSE4705 - HW4: Checkers Representations
   "32-array" Representation - using 3 unsigned ints
------------------------------------------------------*/

#include "checkers32_calc.h"

// Static Function prototypes
// (probably a way to combine white and black specific functions together, as they are incredibly similar)
static void white_moves_helper(unsigned int* moves, unsigned int w_mask, unsigned int k_mask);
static void white_double_moves(unsigned int* moves, unsigned int w_mask, unsigned int k_mask);
static unsigned int black_moves_helper(unsigned int* moves, unsigned int b_mask, unsigned int k_mask);
static unsigned int black_double_moves(unsigned int* moves, unsigned int b_mask, unsigned int k_mask);
static unsigned int find_moves_helper(char* str_moves, unsigned int foe, unsigned int friend, unsigned int k, unsigned short jump_detect_only, unsigned int* k_moves, unsigned int* n_moves, unsigned short plyr);
static void jump_handle(char* str_moves, unsigned int foe, unsigned int friend, unsigned int k, unsigned int* k_moves, unsigned int* n_moves, char* previous_moves, unsigned short plyr);

static unsigned short p_to_r_lookup[32] = {7, 7, 7, 7, 6, 6, 6, 6, 5, 5, 5, 5, 4, 4, 4, 4, 3, 3, 3, 3, 2, 2, 2, 2, 1, 1, 1, 1, 0, 0, 0, 0};
static unsigned short p_to_c_lookup[32] = {1, 3, 5, 7, 0, 2, 4, 6, 1, 3, 5, 7, 0, 2, 4, 6, 1, 3, 5, 7, 0, 2, 4, 6, 1, 3, 5, 7, 0, 2, 4, 6};
static unsigned short bit_count_lookup[256] = {0, 1, 1, 2, 1, 2, 2, 3, 1, 2, 2, 3, 2, 3, 3, 4, 1, 2,
    2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5, 1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5, 2, 3, 3, 4,
    3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6, 1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5, 2, 3, 3, 4, 3, 4,
    4, 5, 3, 4, 4, 5, 4, 5, 5, 6, 2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6, 3, 4, 4, 5, 4, 5, 5, 6,
    4, 5, 5, 6, 5, 6, 6, 7, 1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5, 2, 3, 3, 4, 3, 4, 4, 5, 3, 4,
    4, 5, 4, 5, 5, 6, 2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6, 3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6,
    5, 6, 6, 7, 2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6, 3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6,
    6, 7, 3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7, 4, 5, 5, 6, 5, 6, 6, 7, 5, 6, 6, 7, 6, 7, 7, 8 };

/*--------------------------------------------
// To generate bit_count_lookup table:
// (note that static blocks are not valid c)
//--------------------------------------------
    static {
        for(int i = 0; i < 256; i ++) {
            unsigned short count = 0;
            for (int pos = 0; pos < 8; pos++)
                if (i&(1<<pos)) count++;
            bit_count_lookup[i] = count;
        }
    }
--------------------------------------------*/

// Print the current checkers board
void print_board(unsigned int b, unsigned int w, unsigned int k) {
    // Start iterating from 1st bit
    unsigned int pos = 0x00000001;
    // Iterate over 32 bits
    for (unsigned short i = 1; i <= 32; i++) {
        // Recall:
        // 1: +b+b+b+b -> -1-2-3-4
        // 2: b+b+b+b+ -> 5-6-7-8-
        // 3: +b+b+b+b -> -9-10-11-12
        // 4: -+-+-+-+ -> 13-14-15-16-
        // 5: +-+-+-+- -> -17-18-19-20
        // 6: w+w+w+w+ -> 21-22-23-24-
        // 7: +w+w+w+w -> -25-26-27-28
        // 8: w+w+w+w+ -> 29-30-31-32-

        // "+" means empty non-playable space
        if (pos_to_row(i)%2) // Odd rows, starting from top row as 1st
            printf("+"); // Mark empty position before piece

        // Familiarize yourself with bitwise operators..
        // "w & k" means "white pieces which are king-ed"
        // "pos & .." iterates one bit at a time ( starting at 1st bit counting up)
        if (pos & w & k) printf("W"); // "W" means king-ed white piece
        else if (pos & w) printf("w"); // "w" means normal black piece
        else if (pos & b & k) printf("B"); // "B" means king-ed white piece
        else if (pos & b) printf("b"); // "b" means normal black piece
        else printf("-"); // "-" means empty playable space

        if (!(pos_to_row(i)%2)) // Even rows
            printf("+"); // Mark empty position after piece

        if (i%4==0) // Last piece in row
            printf("\n"); // Print new line

        // Shift the position left one (i.e. 1st bit -> 2nd bit -> etc.)
        pos = pos<<1;
    }
    printf("\n"); // Print new line
}

// Prints values of an individual mask (i.e "print_mask(w)" prints all white pieces)
void print_mask(unsigned int mask) {
    // Start iterating from 1st bit
    unsigned int pos = 0x00000001;
    // Iterate over 32 bits
    for (unsigned short i = 1; i <= 32; i++) {
        if (pos_to_row(i)%2) // Odd rows, starting from top row as 1st
            printf("+"); // Mark empty position before piece

        if (pos & mask) printf("1");
        else printf("0");

        if (!(pos_to_row(i)%2)) // Even rows
            printf("+"); // Mark empty position after piece

        if (i%4==0) // Last piece in row
            printf("\n"); // Print new line

        // Shift the position left one (i.e. 1st bit -> 2nd bit -> etc.)
        pos = pos<<1;
    }
    printf("\n"); // Print new line
}

unsigned short count_bits(unsigned int bits) {
    return bit_count_lookup[(bits>>24)&0xff] + bit_count_lookup[(bits>>16)&0xff] + bit_count_lookup[(bits>>8)&0xff] + bit_count_lookup[bits&0xff];
}

unsigned short pos_to_row(unsigned short pos) {
    // return 7 - (pos - 1) / 4;
    return p_to_r_lookup[pos-1];
}

unsigned short pos_to_col(unsigned short pos) {
    // return 2 * ((pos - 1) % 4) + (pos_to_row(pos) % 2);
    return p_to_c_lookup[pos-1];
}

static void white_moves_helper(unsigned int* moves, unsigned int w_mask, unsigned int k_mask) {
    // In 32-bit array representation, for odd numbered rows:
    // diagonal up-left is -4 positions and up-right is -3 positions.
    moves[0] =  (w_mask & 0x0f0f0f00)>>4; // 0x0f0f0f00 masks odd-row positions that move diagonal up-left
    moves[0] |=  (w_mask & 0x07070700)>>3; // 0x07070700 masks odd-row positions that move diagonal up-right
    // diagonal down-left is +4 positions and down-right is +5 positions.
    // Only king-ed white pieces can move down
    moves[1] =  (w_mask & k_mask & 0x0f0f0f0f)<<4; // 0x0f0f0f0f masks odd-row positions that move diagonal down-left
    moves[1] |=  (w_mask & k_mask & 0x07070707)<<5; // 0x07070707 masks odd-row positions that move diagonal down-right
    // For even numbered rows:
    // diagonal up-left is -5 positions and up-right is -4 positions.
    moves[0] |=  (w_mask & 0xe0e0e0e0)>>5; // 0xe0e0e0e0 masks even-row positions that move diagonal up-left
    moves[0] |=  (w_mask & 0xf0f0f0f0)>>4; // 0xf0f0f0f0 masks even-row positions that move diagonal up-right
    // diagonal down-left is +3 positions and down-right is +4 positions.
    // Only king-ed white pieces can move down
    moves[1] |=  (w_mask & k_mask & 0x00e0e0e0)<<3; // 0x00e0e0e0 masks even-row positions that move diagonal down-left
    moves[1] |=  (w_mask & k_mask & 0x00f0f0f0)<<4; // 0x00f0f0f0 masks even-row positions that move diagonal down-right
}

static void white_double_moves(unsigned int* moves, unsigned int w_mask, unsigned int k_mask) {
    // In 32-bit array representation:
    // double diagonal up-left is -9 positions and up-right is -7 positions.
    moves[0] =  (w_mask & 0xeeeeee00)>>9; // 0xeeeeee00 masks positions that move double diagonal up-left
    moves[0] |=  (w_mask & 0x77777700)>>7; // 0x77777700 masks positions that move double diagonal up-right
    // diagonal down-left is +7 positions and down-right is +9 positions.
    // Only king-ed white pieces can move down
    moves[1] =  (w_mask & k_mask & 0x00eeeeee)<<7; // 0x00eeeeee masks positions that move double diagonal down-left
    moves[1] |=  (w_mask & k_mask & 0x00777777)<<9; // 0x00777777 masks positions that move double diagonal down-right
}

static unsigned int black_moves_helper(unsigned int* moves, unsigned int b_mask, unsigned int k_mask) {
    // In 32-bit array representation, for odd numbered rows:
    // diagonal down-left is +4 positions and down-right is +5 positions.
    moves[0] =  (b_mask & 0x0f0f0f0f)<<4; // 0x0f0f0f0f masks odd-row positions that move diagonal down-left
    moves[0] |=  (b_mask & 0x07070707)<<5; // 0x07070707 masks odd-row positions that move diagonal down-right
    // diagonal up-left is -4 positions and up-right is -3 positions.
    // Only king-ed black pieces can move up
    moves[1] =  (b_mask & k_mask & 0x0f0f0f00)>>4; // 0x0f0f0f00 masks odd-row positions that move diagonal up-left
    moves[1] |=  (b_mask & k_mask & 0x07070700)>>3; // 0x07070700 masks odd-row positions that move diagonal up-right

    // For even numbered rows:
    // diagonal down-left is +3 positions and down-right is +4 positions.
    moves[0] |=  (b_mask & 0x00e0e0e0)<<3; // 0x00e0e0e0 masks even-row positions that move diagonal down-left
    moves[0] |=  (b_mask & 0x00f0f0f0)<<4; // 0x00f0f0f0 masks even-row positions that move diagonal down-right
    // diagonal up-left is -5 positions and up-right is -4 positions.
    // Only king-ed black pieces can move up
    moves[1] |=  (b_mask & k_mask & 0xe0e0e0e0)>>5; // 0xe0e0e0e0 masks even-row positions that move diagonal up-left
    moves[1] |=  (b_mask & k_mask & 0xf0f0f0f0)>>4; // 0xf0f0f0f0 masks even-row positions that move diagonal up-right
}

static unsigned int black_double_moves(unsigned int* moves, unsigned int b_mask, unsigned int k_mask) {
    // In 32-bit array representation:
    // diagonal down-left is +7 positions and down-right is +9 positions.
    moves[0] =  (b_mask & 0x00eeeeee)<<7; // 0x00eeeeee masks positions that move double diagonal down-left
    moves[0] |=  (b_mask & 0x00777777)<<9; // 0x00777777 masks positions that move double diagonal down-right
    // double diagonal up-left is -9 positions and up-right is -7 positions.
    // Only king-ed black pieces can move up
    moves[1] =  (b_mask & k_mask & 0xeeeeee00)>>9; // 0xeeeeee00 masks positions that move double diagonal up-left
    moves[1] |=  (b_mask & k_mask & 0x77777700)>>7; // 0x77777700 masks positions that move double diagonal up-right
}

unsigned int white_moves(char* str_moves, unsigned int b, unsigned int w, unsigned int k) {
    return find_moves_helper(str_moves, b, w, k, 0, (unsigned int*){0}, (unsigned int*){0}, 1);
}

unsigned int black_moves(char* str_moves, unsigned int b, unsigned int w, unsigned int k) {
    return find_moves_helper(str_moves, w, b, k, 0, (unsigned int*){0}, (unsigned int*){0}, 0);
}

// Returns possible moves for plyr as a string in the argument str_moves, as well as a mask of first round moves through normal return
static unsigned int find_moves_helper(char* str_moves, unsigned int foe, unsigned int friend, unsigned int k, unsigned short jump_detect_only, unsigned int* k_moves, unsigned int* n_moves, unsigned short plyr) {
    // We spearate king moves and normal piece moves to simplify later work
    unsigned int king_moves[2];
    unsigned int normal_moves[2];

    // These functions return the available move masks through the first argument
    // e.g. king_moves will contain the foward [0] and backward [1] move masks of all white kings after the first function call
    if(plyr)white_moves_helper(king_moves, friend&k, k);
    else black_moves_helper(king_moves, friend&k, k);
    // Because normal pieces can only move forward, the backward mask (normal_moves[1]) will be empty and can be ignored
    if(plyr)white_moves_helper(normal_moves, friend&~k, 0);
    else black_moves_helper(normal_moves, friend&~k, 0);

    // If any moves are attacking an enemy piece, then find jumping position
    if ((king_moves[0]|normal_moves[0]|king_moves[1]) & foe) {
        unsigned int king_jump_moves[2];
        if(plyr)white_moves_helper(king_jump_moves, king_moves[0]&foe, king_moves[0]);
        else black_moves_helper(king_jump_moves, king_moves[0]&foe, king_moves[0]);
        unsigned int king_jump_moves2[2];
        if(plyr)white_moves_helper(king_jump_moves2, king_moves[1]&foe, king_moves[1]);
        else black_moves_helper(king_jump_moves2, king_moves[1]&foe, king_moves[1]);
        king_jump_moves[0]|=king_jump_moves2[0];
        king_jump_moves[1]|=king_jump_moves2[1];
        unsigned int normal_jump_moves[2];
        if(plyr)white_moves_helper(normal_jump_moves, normal_moves[0]&foe, 0);
        else black_moves_helper(normal_jump_moves, normal_moves[0]&foe, 0);

        // Find double moves to test for jumps
        unsigned int double_king[2];
        if(plyr)white_double_moves(double_king, friend&k, k);
        else black_double_moves(double_king, friend&k, k);
        unsigned int double_normal[2];
        if(plyr)white_double_moves(double_normal, friend&~k, 0);
        else black_double_moves(double_normal, friend&~k, 0);
        king_jump_moves[0]&=double_king[0];
        king_jump_moves[1]&=double_king[1];
        normal_jump_moves[0]&=double_normal[0];

        // Continue with jump calculation if we will not always land on another piece after jumping
        if (jump_detect_only || (king_jump_moves[0] & ~(friend|foe)) || (normal_jump_moves[0] & ~(friend|foe)) || (king_jump_moves[1] & ~(friend|foe))) {
            king_jump_moves[0] = king_jump_moves[0] & ~(friend|foe);
            king_jump_moves[1] = king_jump_moves[1] & ~(friend|foe);
            normal_jump_moves[0] = normal_jump_moves[0] & ~(friend|foe);
            if (jump_detect_only) {
                k_moves[0] = king_jump_moves[0];
                k_moves[1] = king_jump_moves[1];
                n_moves[0] = normal_jump_moves[0];
                return king_jump_moves[0]|king_jump_moves[1]|normal_jump_moves[0];
            }
            jump_handle(str_moves, foe, friend, k, king_jump_moves, normal_jump_moves, (char*){0}, plyr);
            if (jump_detect_only || strlen(str_moves)!=0)
                return king_jump_moves[0]|king_jump_moves[1]|normal_jump_moves[0];
        }
    } else if (jump_detect_only) return 0;

    // Otherwise no jumps were detected so move on to find all simple available moves

    // Start by cutting out any move which lands on another piece
    king_moves[0] = king_moves[0] & ~(friend|foe);
    king_moves[1] = king_moves[1] & ~(friend|foe);
    normal_moves[0] = normal_moves[0] & ~(friend|foe);

    // Start iterating through masks from 1st bit
    unsigned int pos = 0x00000001;
    unsigned int start_moves[2]; // Will hold masks for the starting position of the piece before it moved
    char outstr[999] = {0}; // Used to construct the list of available moves which will be returned through the argument str_moves
    // Iterate over 32 bits
    for (unsigned short i = 1; i <= 32; i++) {
        for (unsigned short t = 0; t < 3; t++) {
            start_moves[0] = 0;
            unsigned int test = normal_moves[0];
            if (t<2) test = king_moves[t];
            if (pos&test) {
                if (t!=1) {
                    if (plyr) black_moves_helper(start_moves, pos&test, 0);
                    else white_moves_helper(start_moves, pos&test, 0);
                } else {
                    if (plyr) white_moves_helper(start_moves, pos&test, 0);
                    else black_moves_helper(start_moves, pos&test, 0);
                }
                // Only friendly moves
                start_moves[0]&=friend;
                if (t < 2) start_moves[0]&=k;
                else start_moves[0]&=~k;
                // Now iterate through all positions which may end at the current position (only 4 for non jump)
                short j[4];
                j[0] = i-4;
                j[2] = i+4;
                if (pos_to_row(i)%2) { // If odd row
                    j[1] = i-3;
                    j[3] = i+5;
                } else {
                    j[1] = i-5;
                    j[3] = i+3;
                }
                for (int n = 0; n < 4; n++)
                    if (j[n]>0 && j[n]<=32) {
                        if ((1<<(j[n]-1))&start_moves[0]) { // If there is a piece at the starting position and it is friendly
                            if (strlen(outstr)!=0)
                                sprintf(outstr, "%s, (%hu:%hu):(%hu:%hu)", outstr, pos_to_row(j[n]), pos_to_col(j[n]), pos_to_row(i), pos_to_col(i));
                            else sprintf(outstr, "(%hu:%hu):(%hu:%hu)", pos_to_row(j[n]), pos_to_col(j[n]), pos_to_row(i), pos_to_col(i));
                        }
                    }
            }
        }
        pos = pos<<1;
    }
    sprintf(str_moves, "%s", outstr);
    return (king_moves[0]|normal_moves[0]|king_moves[1]);
}

static void jump_handle(char* str_moves, unsigned int foe, unsigned int friend, unsigned int k, unsigned int* k_moves, unsigned int* n_moves, char* previous_moves, unsigned short plyr) {
    unsigned int pos = 0x00000001;
    unsigned int start_moves[2];
    char outstr[999] = {0};
    // Iterate over 32 bits
    for (unsigned short i = 1; i <= 32; i++) {
        for(unsigned short t = 0; t < 3; t++) {
            unsigned int test = n_moves[0];
            if (t<2) test = k_moves[t];
            if (pos&test) {
                if (t!=1) {
                    if(plyr)black_double_moves(start_moves, pos&test, 0);
                    else white_double_moves(start_moves, pos&test, 0);
                } else {
                    if(plyr)white_double_moves(start_moves, pos&test, 0);
                    else black_double_moves(start_moves, pos&test, 0);
                }
                start_moves[0]&=friend;
                if (t < 2) start_moves[0]&=k;
                else start_moves[0]&=~k;
                // Now iterate through all positions which may end at the current position (only 4 if all jump)
                short j[4] = {i-9, i-7, i+7, i+9};
                for (int n = 0; n < 4; n++)
                    if (j[n]>0 && j[n]<=32) {
                        if ((1<<(j[n]-1))&start_moves[0]) {
                            unsigned short jumped_pos = 0, new_j = j[n];
                            unsigned int next_jumps;
                            if((t!=1 && plyr) || (t==1 && !plyr)) {
                                if (pos_to_row(new_j)%2) { // If started on odd row
                                    if (new_j-i == 7) jumped_pos |= new_j-3;
                                    else jumped_pos |= new_j-4;
                                } else {
                                    if (new_j-i == 7) jumped_pos |= new_j-4;
                                    else jumped_pos |= new_j-5;
                                }
                            } else {
                                if (pos_to_row(new_j)%2) { // If started on odd row
                                    if (i-new_j == 7) jumped_pos |= i-3;
                                    else jumped_pos |= i-4;
                                } else {
                                    if (i-new_j == 7) jumped_pos |= i-4;
                                    else jumped_pos |= i-5;
                                }
                            }
                            if (foe&(1<<(jumped_pos-1))) { // Only continue if piece jumped an opposite player
                                unsigned int next_k_moves[2] = {0,0};
                                unsigned int next_n_moves[2] = {0,0};

                                // See if we can continuously jump
                                if(t==2) next_jumps = find_moves_helper((char*){0}, foe&~(1<<(jumped_pos-1)), (1<<(i-1)), 0, 1, next_k_moves, next_n_moves, plyr);
                                else next_jumps = find_moves_helper((char*){0}, foe&~(1<<(jumped_pos-1)), (1<<(i-1)), (1<<(i-1)), 1, next_k_moves, next_n_moves, plyr);
                                next_k_moves[0]&=~(friend&~(1<<(i-1)));
                                next_k_moves[1]&=~(friend&~(1<<(i-1)));
                                next_n_moves[0]&=~(friend&~(1<<(i-1)));
                                next_jumps&=~(friend&~(1<<(i-1)));
                                if ((t!=2 && next_jumps) || (t==2 && next_n_moves[0])) {
                                    char newstr[999] = {0};
                                    if (previous_moves!=0 && strlen(previous_moves)!=0)
                                        sprintf(newstr, "%s:(%hu:%hu)", previous_moves, pos_to_row(i), pos_to_col(i));
                                    else
                                        sprintf(newstr, "(%hu:%hu):(%hu:%hu)", pos_to_row(j[n]), pos_to_col(j[n]), pos_to_row(i), pos_to_col(i));
                                    if(t==2)jump_handle(str_moves, foe&~(1<<(jumped_pos-1)), (friend&~(1<<(j[n]-1)))|(1<<(i-1)), k&~(1<<(jumped_pos-1)), (unsigned int[2]){0,0}, next_n_moves, newstr, plyr);
                                    else jump_handle(str_moves, foe&~(1<<(jumped_pos-1)), (friend&~(1<<(j[n]-1)))|(1<<(i-1)), (k&~(1<<(j[n]-1)))|(1<<(i-1))&~(1<<(jumped_pos-1)), next_k_moves, next_n_moves, newstr, plyr);
                                } else {
                                    if (previous_moves!=0 && strlen(previous_moves)!=0) {
                                        if (strlen(outstr)!=0)
                                            sprintf(outstr, "%s, %s:(%hu:%hu)", outstr, previous_moves, pos_to_row(i), pos_to_col(i));
                                        else sprintf(outstr, "%s:(%hu:%hu)", previous_moves, pos_to_row(i), pos_to_col(i));
                                    } else {
                                        if (strlen(outstr)!=0)
                                            sprintf(outstr, "%s, (%hu:%hu):(%hu:%hu)", outstr, pos_to_row(j[n]), pos_to_col(j[n]), pos_to_row(i), pos_to_col(i));
                                        else sprintf(outstr, "(%hu:%hu):(%hu:%hu)", pos_to_row(j[n]), pos_to_col(j[n]), pos_to_row(i), pos_to_col(i));
                                    }
                                }
                            }
                        }
                    }
            }
        }
        pos = pos<<1;
    }
    if (str_moves!=0 && strlen(str_moves)!=0) {
        if (outstr!=0 && strlen(outstr)!=0)
            sprintf(str_moves, "%s, %s", str_moves, outstr);
        else
            sprintf(str_moves, "%s", str_moves);
    }
    else
        sprintf(str_moves, "%s", outstr);
}
