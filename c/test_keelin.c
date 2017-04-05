/*------------------------------------------------------
   Keelin Becker-Wheeler
   CSE4705 - HW4: Checkers Representations
   "32-array" Representation - using 3 unsigned ints
------------------------------------------------------*/




// Not minimized/optimized at all, I am so sorry for you dear reader




#include "test_keelin.h"

// Static Function prototypes
// (probably a way to combine white and black specific functions together, as they are incredibly similar)
static void white_moves_helper(unsigned int* moves, unsigned int w_mask, unsigned int k_mask);
static void white_double_moves(unsigned int* moves, unsigned int w_mask, unsigned int k_mask);
static void white_jump_handle(char* str_moves, unsigned int b, unsigned int w, unsigned int k, unsigned int* k_moves, unsigned int* n_moves, char* previous_moves);
static unsigned int black_moves_helper(unsigned int* moves, unsigned int b_mask, unsigned int k_mask);
static unsigned int black_double_moves(unsigned int* moves, unsigned int b_mask, unsigned int k_mask);
static void black_jump_handle(char* str_moves, unsigned int b, unsigned int w, unsigned int k, unsigned int* k_moves, unsigned int* n_moves, char* previous_moves);

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
        if ((i%8)<5 && (i%8)!=0) // Odd rows, starting from top row as 1st
            printf("+"); // Mark empty position before piece

        // Familiarize yourself with bitwise operators..
        // "w & k" means "white pieces which are king-ed"
        // "pos & .." iterates one bit at a time ( starting at 1st bit counting up)
        if (pos & w & k) printf("W"); // "W" means king-ed white piece
        else if (pos & w) printf("w"); // "w" means normal black piece
        else if (pos & b & k) printf("B"); // "B" means king-ed white piece
        else if (pos & b) printf("b"); // "b" means normal black piece
        else printf("-"); // "-" means empty playable space

        if ((i%8)>=5 || (i%8)==0) // Even rows
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
        if ((i%8)<5 && (i%8)!=0) // Odd rows, starting from top row as 1st
            printf("+"); // Mark empty position before piece

        if (pos & mask) printf("1");
        else printf("0");

        if ((i%8)>=5 || (i%8)==0) // Even rows
            printf("+"); // Mark empty position after piece

        if (i%4==0) // Last piece in row
            printf("\n"); // Print new line

        // Shift the position left one (i.e. 1st bit -> 2nd bit -> etc.)
        pos = pos<<1;
    }
    printf("\n"); // Print new line
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

// Returns possible moves for white as a string in the argument str_moves, as well as a mask of first round moves through normal return
unsigned int white_moves(char* str_moves, unsigned int b, unsigned int w, unsigned int k, unsigned short jump_detect_only, unsigned int* k_moves, unsigned int* n_moves) {
    // We spearate king moves and normal piece moves to simplify later work
    unsigned int king_moves[2];
    unsigned int normal_moves[2];

    // These functions return the available move masks through the first argument
    // e.g. king_moves will contain the foward [0] and backward [1] move masks of all white kings after the first function call
    white_moves_helper(king_moves, w&k, k);
    // Because normal pieces can only move forward, the backward mask (normal_moves[1]) will be empty and can be ignored
    white_moves_helper(normal_moves, w&~k, 0);

    // If any moves are attacking a black piece, then find jumping position
    if ((king_moves[0]|normal_moves[0]|king_moves[1]) & b) {
        unsigned int king_jump_moves[2];
        white_moves_helper(king_jump_moves, king_moves[0]&b, king_moves[0]);
        unsigned int king_jump_moves2[2];
        white_moves_helper(king_jump_moves2, king_moves[1]&b, king_moves[1]);
        king_jump_moves[0]|=king_jump_moves2[0];
        king_jump_moves[1]|=king_jump_moves2[1];
        unsigned int normal_jump_moves[2];
        white_moves_helper(normal_jump_moves, normal_moves[0]&b, 0);

        unsigned int double_king[2];
        white_double_moves(double_king, w&k, k);
        unsigned int double_normal[2];
        white_double_moves(double_normal, w&~k, 0);
        king_jump_moves[0]&=double_king[0];
        king_jump_moves[1]&=double_king[1];
        normal_jump_moves[0]&=double_normal[0];

        // Cannot jump onto a piece
        if (jump_detect_only || (king_jump_moves[0] & ~(b|w)) || (normal_jump_moves[0] & ~(b|w)) || (king_jump_moves[1] & ~(b|w))) {
            // Jump detected
            king_jump_moves[0] = king_jump_moves[0] & ~(b|w);
            king_jump_moves[1] = king_jump_moves[1] & ~(b|w);
            normal_jump_moves[0] = normal_jump_moves[0] & ~(b|w);
            if (jump_detect_only) {
                k_moves[0] = king_jump_moves[0];
                k_moves[1] = king_jump_moves[1];
                n_moves[0] = normal_jump_moves[0];
                return king_jump_moves[0]|king_jump_moves[1]|normal_jump_moves[0];
            }
            white_jump_handle(str_moves, b, w, k, king_jump_moves, normal_jump_moves, (char*){0});
            return king_jump_moves[0]|king_jump_moves[1]|normal_jump_moves[0];
        }
    } else if (jump_detect_only) return 0;

    // Otherwise no jumps were detected so move on to find all simple available moves

    // Start by cutting out any move which lands on another piece
    king_moves[0] = king_moves[0] & ~(b|w);
    king_moves[1] = king_moves[1] & ~(b|w);
    normal_moves[0] = normal_moves[0] & ~(b|w);

    // Start iterating through masks from 1st bit
    unsigned int pos = 0x00000001;
    unsigned int start_moves[2]; // Will hold masks for the starting position of the piece before it moved
    char outstr[999] = {0}; // Used to construct the list of available moves which will be returned through the argument str_moves
    // Iterate over 32 bits
    for (unsigned short i = 1; i <= 32; i++) {
        if (pos&king_moves[0]) { // If a white king is able to move forward to the current position
            // Calculate the start position of the white king (use black_move_helper to move backward for white)
            black_moves_helper(start_moves, pos&king_moves[0], 0);
            // Now iterate through all positions which may end at the current position
            // (Can be simplified greatly, i.e. should only be two possible positions so no need to loop over all 32 bits)
            unsigned int npos = 0x00000001;
            for (unsigned short j = 1; j <= 32; j++) {
                if (npos&start_moves[0]&w) { // If there is a piece at the starting position and it is white
                    if (strlen(outstr)!=0)
                        sprintf(outstr, "%s, (%hu:%hu):(%hu:%hu)", outstr, 7-(j-1)/4, 2*((j-1)%4) + ((7-(j-1)/4)%2==0 ? 0 : 1), 7-(i-1)/4, 2*((i-1)%4) + ((7-(i-1)/4)%2==0 ? 0 : 1));
                    else sprintf(outstr, "(%hu:%hu):(%hu:%hu)", 7-(j-1)/4, 2*((j-1)%4) + ((7-(j-1)/4)%2==0 ? 0 : 1), 7-(i-1)/4, 2*((i-1)%4) + ((7-(i-1)/4)%2==0 ? 0 : 1));
                }
                npos = npos<<1;
            }
        } else if (pos&king_moves[1]) {
            white_moves_helper(start_moves, pos&king_moves[1], 0);
            unsigned int npos = 0x00000001;
            for (unsigned short j = 1; j <= 32; j++) {
                if (npos&start_moves[0]&w) {
                    if (strlen(outstr)!=0)
                        sprintf(outstr, "%s, (%hu:%hu):(%hu:%hu)", outstr, 7-(j-1)/4, 2*((j-1)%4) + ((7-(j-1)/4)%2==0 ? 0 : 1), 7-(i-1)/4, 2*((i-1)%4) + ((7-(i-1)/4)%2==0 ? 0 : 1));
                    else sprintf(outstr, "(%hu:%hu):(%hu:%hu)", 7-(j-1)/4, 2*((j-1)%4) + ((7-(j-1)/4)%2==0 ? 0 : 1), 7-(i-1)/4, 2*((i-1)%4) + ((7-(i-1)/4)%2==0 ? 0 : 1));
                }
                npos = npos<<1;
            }
        } else if (pos&normal_moves[0]) {
            black_moves_helper(start_moves, pos&normal_moves[0], 0);
            unsigned int npos = 0x00000001;
            for (unsigned short j = 1; j <= 32; j++) {
                if (npos&start_moves[0]&w) {
                    if (strlen(outstr)!=0)
                        sprintf(outstr, "%s, (%hu:%hu):(%hu:%hu)", outstr, 7-(j-1)/4, 2*((j-1)%4) + ((7-(j-1)/4)%2==0 ? 0 : 1), 7-(i-1)/4, 2*((i-1)%4) + ((7-(i-1)/4)%2==0 ? 0 : 1));
                    else sprintf(outstr, "(%hu:%hu):(%hu:%hu)", 7-(j-1)/4, 2*((j-1)%4) + ((7-(j-1)/4)%2==0 ? 0 : 1), 7-(i-1)/4, 2*((i-1)%4) + ((7-(i-1)/4)%2==0 ? 0 : 1));
                }
                npos = npos<<1;
            }
        }
        pos = pos<<1;
    }
    // fprintf(stdout, "%s\n", outstr);
    sprintf(str_moves, "%s", outstr);
    return (king_moves[0]|normal_moves[0]|king_moves[1]);
}

static void white_jump_handle(char* str_moves, unsigned int b, unsigned int w, unsigned int k, unsigned int* k_moves, unsigned int* n_moves, char* previous_moves) {
    // fprintf(stdout, "test\n");
    // print_mask(k_moves[0]);
    // print_mask(k_moves[1]);
    // print_mask(n_moves[0]);
    // fprintf(stdout, "done\n");

    unsigned int pos = 0x00000001;
    unsigned int start_moves[2];
    char outstr[999] = {0};
    // Iterate over 32 bits
    for (unsigned short i = 1; i <= 32; i++) {
        if (pos&k_moves[0]) {
            black_double_moves(start_moves, pos&k_moves[0], 0);
            unsigned int npos = 0x00000001;
            for (unsigned short j = 1; j <= 32; j++) {
                if (npos&start_moves[0]&w) {
                    unsigned short jumped_pos = 0, new_j = j;
                    unsigned int next_jumps;
                    if ((new_j%8<5) && (new_j%8!=0)) { // If started on odd row
                        if (new_j-i == 7) jumped_pos |= new_j-3;
                        else jumped_pos |= new_j-4;
                    } else {
                        if (new_j-i == 7) jumped_pos |= new_j-4;
                        else jumped_pos |= new_j-5;
                    }
                    if(b&(1<<(jumped_pos-1))) { // Only continue if piece jumped an opposite player
                        // fprintf(stdout, "multi-jump:%d\n", jumped_pos);
                        unsigned int next_k_moves[2] = {0,0};
                        unsigned int next_n_moves[2] = {0,0};
                        next_jumps = white_moves((char*){0}, b&~(1<<(jumped_pos-1)), (1<<(i-1)), (1<<(i-1)), 1, next_k_moves, next_n_moves);
                        if (next_jumps) {
                            char newstr[999] = {0};
                            if (previous_moves!=0 && strlen(previous_moves)!=0)
                                sprintf(newstr, "%s:(%hu:%hu)", previous_moves, 7-(i-1)/4, 2*((i-1)%4) + ((7-(i-1)/4)%2==0 ? 0 : 1));
                            else
                                sprintf(newstr, "(%hu:%hu):(%hu:%hu)", 7-(j-1)/4, 2*((j-1)%4) + ((7-(j-1)/4)%2==0 ? 0 : 1), 7-(i-1)/4, 2*((i-1)%4) + ((7-(i-1)/4)%2==0 ? 0 : 1));
                            white_jump_handle(str_moves, b&~(1<<(jumped_pos-1)), (w&~(1<<(j-1)))|(1<<(i-1)), (k&~(1<<(j-1)))|(1<<(i-1))&~(1<<(jumped_pos-1)), next_k_moves, next_n_moves, newstr);
                        } else {
                            if (previous_moves!=0 && strlen(previous_moves)!=0) {
                                if (strlen(outstr)!=0)
                                    sprintf(outstr, "%s, %s:(%hu:%hu)", outstr, previous_moves, 7-(i-1)/4, 2*((i-1)%4) + ((7-(i-1)/4)%2==0 ? 0 : 1));
                                else sprintf(outstr, "%s:(%hu:%hu)", previous_moves, 7-(i-1)/4, 2*((i-1)%4) + ((7-(i-1)/4)%2==0 ? 0 : 1));
                            } else {
                                if (strlen(outstr)!=0)
                                    sprintf(outstr, "%s, (%hu:%hu):(%hu:%hu)", outstr, 7-(j-1)/4, 2*((j-1)%4) + ((7-(j-1)/4)%2==0 ? 0 : 1), 7-(i-1)/4, 2*((i-1)%4) + ((7-(i-1)/4)%2==0 ? 0 : 1));
                                else sprintf(outstr, "(%hu:%hu):(%hu:%hu)", 7-(j-1)/4, 2*((j-1)%4) + ((7-(j-1)/4)%2==0 ? 0 : 1), 7-(i-1)/4, 2*((i-1)%4) + ((7-(i-1)/4)%2==0 ? 0 : 1));
                            }
                        }
                    }
                }
                npos = npos<<1;
            }
        } else if (pos&k_moves[1]) {
            white_double_moves(start_moves, pos&k_moves[1], 0);
            unsigned int npos = 0x00000001;
            for (unsigned short j = 1; j <= 32; j++) {
                if (npos&start_moves[0]&w) {
                    unsigned short jumped_pos = 0, new_j = j;
                    unsigned int next_jumps;
                    if ((new_j%8<5) && (new_j%8!=0)) { // If started on odd row
                        if (i-new_j == 7) jumped_pos |= i-3;
                        else jumped_pos |= i-4;
                    } else {
                        if (i-new_j == 7) jumped_pos |= i-4;
                        else jumped_pos |= i-5;
                    }
                    if(b&(1<<(jumped_pos-1))) { // Only continue if piece jumped an opposite player
                        // fprintf(stdout, "multi-jump:%d\n", jumped_pos);
                        unsigned int next_k_moves[2] = {0,0};
                        unsigned int next_n_moves[2] = {0,0};
                        next_jumps = white_moves((char*){0}, b&~(1<<(jumped_pos-1)), (1<<(i-1)), (1<<(i-1)), 1, next_k_moves, next_n_moves);
                        if (next_jumps) {
                            char newstr[999] = {0};
                            if (previous_moves!=0 && strlen(previous_moves)!=0)
                                sprintf(newstr, "%s:(%hu:%hu)", previous_moves, 7-(i-1)/4, 2*((i-1)%4) + ((7-(i-1)/4)%2==0 ? 0 : 1));
                            else
                                sprintf(newstr, "(%hu:%hu):(%hu:%hu)", 7-(j-1)/4, 2*((j-1)%4) + ((7-(j-1)/4)%2==0 ? 0 : 1), 7-(i-1)/4, 2*((i-1)%4) + ((7-(i-1)/4)%2==0 ? 0 : 1));
                            white_jump_handle(str_moves, b&~(1<<(jumped_pos-1)), (w&~(1<<(j-1)))|(1<<(i-1)), (k&~(1<<(j-1)))|(1<<(i-1))&~(1<<(jumped_pos-1)), next_k_moves, next_n_moves, newstr);
                        } else {
                            if (previous_moves!=0 && strlen(previous_moves)!=0) {
                                if (strlen(outstr)!=0)
                                    sprintf(outstr, "%s, %s:(%hu:%hu)", outstr, previous_moves, 7-(i-1)/4, 2*((i-1)%4) + ((7-(i-1)/4)%2==0 ? 0 : 1));
                                else sprintf(outstr, "%s:(%hu:%hu)", previous_moves, 7-(i-1)/4, 2*((i-1)%4) + ((7-(i-1)/4)%2==0 ? 0 : 1));
                            } else {
                                if (strlen(outstr)!=0)
                                    sprintf(outstr, "%s, (%hu:%hu):(%hu:%hu)", outstr, 7-(j-1)/4, 2*((j-1)%4) + ((7-(j-1)/4)%2==0 ? 0 : 1), 7-(i-1)/4, 2*((i-1)%4) + ((7-(i-1)/4)%2==0 ? 0 : 1));
                                else sprintf(outstr, "(%hu:%hu):(%hu:%hu)", 7-(j-1)/4, 2*((j-1)%4) + ((7-(j-1)/4)%2==0 ? 0 : 1), 7-(i-1)/4, 2*((i-1)%4) + ((7-(i-1)/4)%2==0 ? 0 : 1));
                            }
                        }
                    }
                }
                npos = npos<<1;
            }
        } else if (pos&n_moves[0]) {
            black_double_moves(start_moves, pos&n_moves[0], 0);
            unsigned int npos = 0x00000001;
            for (unsigned short j = 1; j <= 32; j++) {
                if (npos&start_moves[0]&w) {
                    unsigned short jumped_pos = 0, new_j = j;
                    unsigned int next_jumps;
                    if ((new_j%8<5) && (new_j%8!=0)) { // If started on odd row
                        if (new_j-i == 7) jumped_pos |= new_j-3;
                        else jumped_pos |= new_j-4;
                    } else {
                        if (new_j-i == 7) jumped_pos |= new_j-4;
                        else jumped_pos |= new_j-5;
                    }
                    if(b&(1<<(jumped_pos-1))) { // Only continue if piece jumped an opposite player
                        // fprintf(stdout, "multi-jump:%d\n", jumped_pos);
                        unsigned int next_k_moves[2] = {0,0};
                        unsigned int next_n_moves[2] = {0,0};
                        next_jumps = white_moves((char*){0}, b&~(1<<(jumped_pos-1)), (1<<(i-1)), (1<<(i-1)), 1, next_k_moves, next_n_moves);
                        if (next_n_moves[0]) {
                            char newstr[999] = {0};
                            if (previous_moves!=0 && strlen(previous_moves)!=0)
                                sprintf(newstr, "%s:(%hu:%hu)", previous_moves, 7-(i-1)/4, 2*((i-1)%4) + ((7-(i-1)/4)%2==0 ? 0 : 1));
                            else
                                sprintf(newstr, "(%hu:%hu):(%hu:%hu)", 7-(j-1)/4, 2*((j-1)%4) + ((7-(j-1)/4)%2==0 ? 0 : 1), 7-(i-1)/4, 2*((i-1)%4) + ((7-(i-1)/4)%2==0 ? 0 : 1));
                            white_jump_handle(str_moves, b&~(1<<(jumped_pos-1)), (w&~(1<<(j-1)))|(1<<(i-1)), (k&~(1<<(j-1)))|(1<<(i-1))&~(1<<(jumped_pos-1)), (unsigned int[2]){0,0}, next_n_moves, newstr);
                        } else {
                            if (previous_moves!=0 && strlen(previous_moves)!=0) {
                                if (strlen(outstr)!=0)
                                    sprintf(outstr, "%s, %s:(%hu:%hu)", outstr, previous_moves, 7-(i-1)/4, 2*((i-1)%4) + ((7-(i-1)/4)%2==0 ? 0 : 1));
                                else sprintf(outstr, "%s:(%hu:%hu)", previous_moves, 7-(i-1)/4, 2*((i-1)%4) + ((7-(i-1)/4)%2==0 ? 0 : 1));
                            } else {
                                if (strlen(outstr)!=0)
                                    sprintf(outstr, "%s, (%hu:%hu):(%hu:%hu)", outstr, 7-(j-1)/4, 2*((j-1)%4) + ((7-(j-1)/4)%2==0 ? 0 : 1), 7-(i-1)/4, 2*((i-1)%4) + ((7-(i-1)/4)%2==0 ? 0 : 1));
                                else sprintf(outstr, "(%hu:%hu):(%hu:%hu)", 7-(j-1)/4, 2*((j-1)%4) + ((7-(j-1)/4)%2==0 ? 0 : 1), 7-(i-1)/4, 2*((i-1)%4) + ((7-(i-1)/4)%2==0 ? 0 : 1));
                            }
                        }
                    }
                }
                npos = npos<<1;
            }
        }
        pos = pos<<1;
    }
    // fprintf(stdout, "%s\n", outstr);
    if (str_moves!=0 && strlen(str_moves)!=0) {
        if (outstr!=0 && strlen(outstr)!=0)
            sprintf(str_moves, "%s, %s", str_moves, outstr);
        else
            sprintf(str_moves, "%s", str_moves);
    }
    else
        sprintf(str_moves, "%s", outstr);
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

// Returns possible moves for black as a string in the argument str_moves, as well as a mask of first round moves through normal return
unsigned int black_moves(char* str_moves, unsigned int b, unsigned int w, unsigned int k, unsigned short jump_detect_only, unsigned int* k_moves, unsigned int* n_moves) {
    unsigned int king_moves[2];
    black_moves_helper(king_moves, b&k, k);
    unsigned int normal_moves[2];
    black_moves_helper(normal_moves, b&~k, 0);

    // If any moves are attacking a white piece, then find jumping position
    if ((king_moves[0]|normal_moves[0]|king_moves[1]) & w) {
        unsigned int king_jump_moves[2];
        black_moves_helper(king_jump_moves, king_moves[0]&w, king_moves[0]);
        unsigned int king_jump_moves2[2];
        black_moves_helper(king_jump_moves2, king_moves[1]&w, king_moves[1]);
        king_jump_moves[0]|=king_jump_moves2[0];
        king_jump_moves[1]|=king_jump_moves2[1];
        unsigned int normal_jump_moves[2];
        black_moves_helper(normal_jump_moves, normal_moves[0]&w, 0);

        unsigned int double_king[2];
        black_double_moves(double_king, b&k, k);
        unsigned int double_normal[2];
        black_double_moves(double_normal, b&~k, 0);
        king_jump_moves[0]&=double_king[0];
        king_jump_moves[1]&=double_king[1];
        normal_jump_moves[0]&=double_normal[0];

        // Cannot jump onto a piece
        if (jump_detect_only || (king_jump_moves[0] & ~(b|w)) || (normal_jump_moves[0] & ~(b|w)) || (king_jump_moves[1] & ~(b|w))) {
            // Jump detected
            king_jump_moves[0] = king_jump_moves[0] & ~(b|w);
            king_jump_moves[1] = king_jump_moves[1] & ~(b|w);
            normal_jump_moves[0] = normal_jump_moves[0] & ~(b|w);
            if (jump_detect_only) {
                k_moves[0] = king_jump_moves[0];
                k_moves[1] = king_jump_moves[1];
                n_moves[0] = normal_jump_moves[0];
                return king_jump_moves[0]|king_jump_moves[1]|normal_jump_moves[0];
            }
            black_jump_handle(str_moves, b, w, k, king_jump_moves, normal_jump_moves, (char*){0});
            return king_jump_moves[0]|king_jump_moves[1]|normal_jump_moves[0];
        }
    } else if (jump_detect_only) return 0;

    king_moves[0] = king_moves[0] & ~(b|w);
    king_moves[1] = king_moves[1] & ~(b|w);
    normal_moves[0] = normal_moves[0] & ~(b|w);

    // Start iterating from 1st bit
    unsigned int pos = 0x00000001;
    unsigned int start_moves[2];
    char outstr[999] = {0};
    // Iterate over 32 bits
    for (unsigned short i = 1; i <= 32; i++) {
        if (pos&king_moves[0]) {
            white_moves_helper(start_moves, pos&king_moves[0], 0);
            unsigned int npos = 0x00000001;
            for (unsigned short j = 1; j <= 32; j++) {
                if (npos&start_moves[0]&b) {
                    if (strlen(outstr)!=0)
                        sprintf(outstr, "%s, (%hu:%hu):(%hu:%hu)", outstr, 7-(j-1)/4, 2*((j-1)%4) + ((7-(j-1)/4)%2==0 ? 0 : 1), 7-(i-1)/4, 2*((i-1)%4) + ((7-(i-1)/4)%2==0 ? 0 : 1));
                    else sprintf(outstr, "(%hu:%hu):(%hu:%hu)", 7-(j-1)/4, 2*((j-1)%4) + ((7-(j-1)/4)%2==0 ? 0 : 1), 7-(i-1)/4, 2*((i-1)%4) + ((7-(i-1)/4)%2==0 ? 0 : 1));
                }
                npos = npos<<1;
            }
        } else if (pos&king_moves[1]) {
            black_moves_helper(start_moves, pos&king_moves[1], 0);
            unsigned int npos = 0x00000001;
            for (unsigned short j = 1; j <= 32; j++) {
                if (npos&start_moves[0]&b) {
                    if (strlen(outstr)!=0)
                        sprintf(outstr, "%s, (%hu:%hu):(%hu:%hu)", outstr, 7-(j-1)/4, 2*((j-1)%4) + ((7-(j-1)/4)%2==0 ? 0 : 1), 7-(i-1)/4, 2*((i-1)%4) + ((7-(i-1)/4)%2==0 ? 0 : 1));
                    else sprintf(outstr, "(%hu:%hu):(%hu:%hu)", 7-(j-1)/4, 2*((j-1)%4) + ((7-(j-1)/4)%2==0 ? 0 : 1), 7-(i-1)/4, 2*((i-1)%4) + ((7-(i-1)/4)%2==0 ? 0 : 1));
                }
                npos = npos<<1;
            }
        } else if (pos&normal_moves[0]) {
            white_moves_helper(start_moves, pos&normal_moves[0], 0);
            unsigned int npos = 0x00000001;
            for (unsigned short j = 1; j <= 32; j++) {
                if (npos&start_moves[0]&b) {
                    if (strlen(outstr)!=0)
                        sprintf(outstr, "%s, (%hu:%hu):(%hu:%hu)", outstr, 7-(j-1)/4, 2*((j-1)%4) + ((7-(j-1)/4)%2==0 ? 0 : 1), 7-(i-1)/4, 2*((i-1)%4) + ((7-(i-1)/4)%2==0 ? 0 : 1));
                    else sprintf(outstr, "(%hu:%hu):(%hu:%hu)", 7-(j-1)/4, 2*((j-1)%4) + ((7-(j-1)/4)%2==0 ? 0 : 1), 7-(i-1)/4, 2*((i-1)%4) + ((7-(i-1)/4)%2==0 ? 0 : 1));
                }
                npos = npos<<1;
            }
        }
        pos = pos<<1;
    }
    // fprintf(stdout, "%s\n", outstr);
    sprintf(str_moves, "%s", outstr);
    return (king_moves[0]|normal_moves[0]|king_moves[1]);
}

static void black_jump_handle(char* str_moves, unsigned int b, unsigned int w, unsigned int k, unsigned int* k_moves, unsigned int* n_moves, char* previous_moves) {
    // fprintf(stdout, "test\n");
    // print_mask(k_moves[0]);
    // print_mask(k_moves[1]);
    // print_mask(n_moves[0]);
    // fprintf(stdout, "done\n");

    unsigned int pos = 0x00000001;
    unsigned int start_moves[2];
    char outstr[999] = {0};
    // Iterate over 32 bits
    for (unsigned short i = 1; i <= 32; i++) {
        if (pos&k_moves[0]) {
            white_double_moves(start_moves, pos&k_moves[0], 0);
            unsigned int npos = 0x00000001;
            for (unsigned short j = 1; j <= 32; j++) {
                if (npos&start_moves[0]&b) {
                    unsigned short jumped_pos = 0, new_j = j;
                    unsigned int next_jumps;
                    if ((new_j%8<5) && (new_j%8!=0)) { // If started on odd row
                        if (i-new_j == 7) jumped_pos |= i-3;
                        else jumped_pos |= i-4;
                    } else {
                        if (i-new_j == 7) jumped_pos |= i-4;
                        else jumped_pos |= i-5;
                    }
                    if(w&(1<<(jumped_pos-1))) { // Only continue if piece jumped an opposite player
                        // fprintf(stdout, "multi-jump:%d\n", jumped_pos);
                        unsigned int next_k_moves[2] = {0,0};
                        unsigned int next_n_moves[2] = {0,0};
                        next_jumps = black_moves((char*){0}, (1<<(i-1)), w&~(1<<(jumped_pos-1)), (1<<(i-1)), 1, next_k_moves, next_n_moves);
                        if (next_jumps) {
                            char newstr[999] = {0};
                            if (previous_moves!=0 && strlen(previous_moves)!=0)
                                sprintf(newstr, "%s:(%hu:%hu)", previous_moves, 7-(i-1)/4, 2*((i-1)%4) + ((7-(i-1)/4)%2==0 ? 0 : 1));
                            else
                                sprintf(newstr, "(%hu:%hu):(%hu:%hu)", 7-(j-1)/4, 2*((j-1)%4) + ((7-(j-1)/4)%2==0 ? 0 : 1), 7-(i-1)/4, 2*((i-1)%4) + ((7-(i-1)/4)%2==0 ? 0 : 1));
                            black_jump_handle(str_moves, (b&~(1<<(j-1)))|(1<<(i-1)), w&~(1<<(jumped_pos-1)), (k&~(1<<(j-1)))|(1<<(i-1))&~(1<<(jumped_pos-1)), next_k_moves, next_n_moves, newstr);
                        } else {
                            if (previous_moves!=0 && strlen(previous_moves)!=0) {
                                if (strlen(outstr)!=0)
                                    sprintf(outstr, "%s, %s:(%hu:%hu)", outstr, previous_moves, 7-(i-1)/4, 2*((i-1)%4) + ((7-(i-1)/4)%2==0 ? 0 : 1));
                                else sprintf(outstr, "%s:(%hu:%hu)", previous_moves, 7-(i-1)/4, 2*((i-1)%4) + ((7-(i-1)/4)%2==0 ? 0 : 1));
                            } else {
                                if (strlen(outstr)!=0)
                                    sprintf(outstr, "%s, (%hu:%hu):(%hu:%hu)", outstr, 7-(j-1)/4, 2*((j-1)%4) + ((7-(j-1)/4)%2==0 ? 0 : 1), 7-(i-1)/4, 2*((i-1)%4) + ((7-(i-1)/4)%2==0 ? 0 : 1));
                                else sprintf(outstr, "(%hu:%hu):(%hu:%hu)", 7-(j-1)/4, 2*((j-1)%4) + ((7-(j-1)/4)%2==0 ? 0 : 1), 7-(i-1)/4, 2*((i-1)%4) + ((7-(i-1)/4)%2==0 ? 0 : 1));
                            }
                        }
                    }
                }
                npos = npos<<1;
            }
        } else if (pos&k_moves[1]) {
            black_double_moves(start_moves, pos&k_moves[1], 0);
            unsigned int npos = 0x00000001;
            for (unsigned short j = 1; j <= 32; j++) {
                if (npos&start_moves[0]&b) {
                    unsigned short jumped_pos = 0, new_j = j;
                    unsigned int next_jumps;
                    if ((new_j%8<5) && (new_j%8!=0)) { // If started on odd row
                        if (new_j-i == 7) jumped_pos |= new_j-3;
                        else jumped_pos |= new_j-4;
                    } else {
                        if (new_j-i == 7) jumped_pos |= new_j-4;
                        else jumped_pos |= new_j-5;
                    }
                    if(w&(1<<(jumped_pos-1))) { // Only continue if piece jumped an opposite player
                        // fprintf(stdout, "multi-jump:%d\n", jumped_pos);
                        unsigned int next_k_moves[2] = {0,0};
                        unsigned int next_n_moves[2] = {0,0};
                        next_jumps = black_moves((char*){0}, (1<<(i-1)), w&~(1<<(jumped_pos-1)), (1<<(i-1)), 1, next_k_moves, next_n_moves);
                        if (next_jumps) {
                            char newstr[999] = {0};
                            if (previous_moves!=0 && strlen(previous_moves)!=0)
                                sprintf(newstr, "%s:(%hu:%hu)", previous_moves, 7-(i-1)/4, 2*((i-1)%4) + ((7-(i-1)/4)%2==0 ? 0 : 1));
                            else
                                sprintf(newstr, "(%hu:%hu):(%hu:%hu)", 7-(j-1)/4, 2*((j-1)%4) + ((7-(j-1)/4)%2==0 ? 0 : 1), 7-(i-1)/4, 2*((i-1)%4) + ((7-(i-1)/4)%2==0 ? 0 : 1));
                            black_jump_handle(str_moves, (b&~(1<<(j-1)))|(1<<(i-1)), w&~(1<<(jumped_pos-1)), (k&~(1<<(j-1)))|(1<<(i-1))&~(1<<(jumped_pos-1)), next_k_moves, next_n_moves, newstr);
                        } else {
                            if (previous_moves!=0 && strlen(previous_moves)!=0) {
                                if (strlen(outstr)!=0)
                                    sprintf(outstr, "%s, %s:(%hu:%hu)", outstr, previous_moves, 7-(i-1)/4, 2*((i-1)%4) + ((7-(i-1)/4)%2==0 ? 0 : 1));
                                else sprintf(outstr, "%s:(%hu:%hu)", previous_moves, 7-(i-1)/4, 2*((i-1)%4) + ((7-(i-1)/4)%2==0 ? 0 : 1));
                            } else {
                                if (strlen(outstr)!=0)
                                    sprintf(outstr, "%s, (%hu:%hu):(%hu:%hu)", outstr, 7-(j-1)/4, 2*((j-1)%4) + ((7-(j-1)/4)%2==0 ? 0 : 1), 7-(i-1)/4, 2*((i-1)%4) + ((7-(i-1)/4)%2==0 ? 0 : 1));
                                else sprintf(outstr, "(%hu:%hu):(%hu:%hu)", 7-(j-1)/4, 2*((j-1)%4) + ((7-(j-1)/4)%2==0 ? 0 : 1), 7-(i-1)/4, 2*((i-1)%4) + ((7-(i-1)/4)%2==0 ? 0 : 1));
                            }
                        }
                    }
                }
                npos = npos<<1;
            }
        } else if (pos&n_moves[0]) {
            white_double_moves(start_moves, pos&n_moves[0], 0);
            unsigned int npos = 0x00000001;
            for (unsigned short j = 1; j <= 32; j++) {
                if (npos&start_moves[0]&b) {
                    unsigned short jumped_pos = 0, new_j = j;
                    unsigned int next_jumps;
                    if ((new_j%8<5) && (new_j%8!=0)) { // If started on odd row
                        if (i-new_j == 7) jumped_pos |= i-3;
                        else jumped_pos |= i-4;
                    } else {
                        if (i-new_j == 7) jumped_pos |= i-4;
                        else jumped_pos |= i-5;
                    }
                    if(w&(1<<(jumped_pos-1))) { // Only continue if piece jumped an opposite player
                        // fprintf(stdout, "multi-jump:%d\n", jumped_pos);
                        unsigned int next_k_moves[2] = {0,0};
                        unsigned int next_n_moves[2] = {0,0};
                        next_jumps = black_moves((char*){0}, (1<<(i-1)), w&~(1<<(jumped_pos-1)), (1<<(i-1)), 1, next_k_moves, next_n_moves);
                        if (next_n_moves[0]) {
                            char newstr[999] = {0};
                            if (previous_moves!=0 && strlen(previous_moves)!=0)
                                sprintf(newstr, "%s:(%hu:%hu)", previous_moves, 7-(i-1)/4, 2*((i-1)%4) + ((7-(i-1)/4)%2==0 ? 0 : 1));
                            else
                                sprintf(newstr, "(%hu:%hu):(%hu:%hu)", 7-(j-1)/4, 2*((j-1)%4) + ((7-(j-1)/4)%2==0 ? 0 : 1), 7-(i-1)/4, 2*((i-1)%4) + ((7-(i-1)/4)%2==0 ? 0 : 1));
                            black_jump_handle(str_moves, (b&~(1<<(j-1)))|(1<<(i-1)), w&~(1<<(jumped_pos-1)), (k&~(1<<(j-1)))|(1<<(i-1))&~(1<<(jumped_pos-1)), (unsigned int[2]){0,0}, next_n_moves, newstr);
                        } else {
                            if (previous_moves!=0 && strlen(previous_moves)!=0) {
                                if (strlen(outstr)!=0)
                                    sprintf(outstr, "%s, %s:(%hu:%hu)", outstr, previous_moves, 7-(i-1)/4, 2*((i-1)%4) + ((7-(i-1)/4)%2==0 ? 0 : 1));
                                else sprintf(outstr, "%s:(%hu:%hu)", previous_moves, 7-(i-1)/4, 2*((i-1)%4) + ((7-(i-1)/4)%2==0 ? 0 : 1));
                            } else {
                                if (strlen(outstr)!=0)
                                    sprintf(outstr, "%s, (%hu:%hu):(%hu:%hu)", outstr, 7-(j-1)/4, 2*((j-1)%4) + ((7-(j-1)/4)%2==0 ? 0 : 1), 7-(i-1)/4, 2*((i-1)%4) + ((7-(i-1)/4)%2==0 ? 0 : 1));
                                else sprintf(outstr, "(%hu:%hu):(%hu:%hu)", 7-(j-1)/4, 2*((j-1)%4) + ((7-(j-1)/4)%2==0 ? 0 : 1), 7-(i-1)/4, 2*((i-1)%4) + ((7-(i-1)/4)%2==0 ? 0 : 1));
                            }
                        }
                    }
                }
                npos = npos<<1;
            }
        }
        pos = pos<<1;
    }
    // fprintf(stdout, "%s\n", outstr);
    if (str_moves!=0 && strlen(str_moves)!=0) {
        if (outstr!=0 && strlen(outstr)!=0)
            sprintf(str_moves, "%s, %s", str_moves, outstr);
        else
            sprintf(str_moves, "%s", str_moves);
    }
    else
        sprintf(str_moves, "%s", outstr);
}
