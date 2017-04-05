/*------------------------------------------------------
   Keelin Becker-Wheeler
   CSE4705 - HW4: Checkers Representations
   "32-array" Representation - using 3 unsigned ints
------------------------------------------------------*/
#ifndef TEST_KEELIN_H
#define TEST_KEELIN_H

#include "keelin_board.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Function prototypes
void print_board(unsigned int b, unsigned int w, unsigned int k);
void print_mask(unsigned int mask);
Move* white_moves(unsigned int b, unsigned int w, unsigned int k, unsigned short jump_detect_only, unsigned int* k_moves, unsigned int* n_moves);
Move* black_moves(unsigned int b, unsigned int w, unsigned int k, unsigned short jump_detect_only, unsigned int* k_moves, unsigned int* n_moves);

#endif
