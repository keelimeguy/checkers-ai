/*------------------------------------------------------
   Keelin Becker-Wheeler
   CSE4705 - HW4: Checkers Representations
   "32-array" Representation - using 3 unsigned ints
------------------------------------------------------*/
#ifndef TEST_KEELIN_H
#define TEST_KEELIN_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Function prototypes
void print_board(unsigned int b, unsigned int w, unsigned int k);
void print_mask(unsigned int mask);
unsigned int white_moves(char* str_moves, unsigned int b, unsigned int w, unsigned int k, unsigned short jump_detect_only, unsigned int* k_moves, unsigned int* n_moves);
unsigned int black_moves(char* str_moves, unsigned int b, unsigned int w, unsigned int k, unsigned short jump_detect_only, unsigned int* k_moves, unsigned int* n_moves);

#endif
