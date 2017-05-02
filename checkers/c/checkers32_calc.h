/*------------------------------------------------------
   Keelin Becker-Wheeler
   CSE4705 - HW4: Checkers Representations
   "32-array" Representation - using 3 unsigned ints
------------------------------------------------------*/
#ifndef CHECKERS32_CALC_H
#define CHECKERS32_CALC_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define OUTSTR_SIZE 999

// Function prototypes
unsigned short count_bits(unsigned int bits);
void print_board(unsigned int b, unsigned int w, unsigned int k);
void print_mask(unsigned int mask);
unsigned short pos_to_row(unsigned short pos);
unsigned short pos_to_col(unsigned short pos);
unsigned int white_moves(char* str_moves, unsigned int b, unsigned int w, unsigned int k);
unsigned int black_moves(char* str_moves, unsigned int b, unsigned int w, unsigned int k);

#endif
