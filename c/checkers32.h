#ifndef CHECKERS32_H
#define CHECKERS32_H

#include "checkers32_calc.h"

typedef struct Board {
    unsigned int b, w, k;
    unsigned short plyr;
} Board;

typedef struct Move {
    unsigned short* route;
    int length;
} Move;

/* void setup(unsigned int b, unsigned int w, unsigned int k, unsigned short plyr); */

Board* Board_alloc();
void Board_destroy(Board* b);

Move* Move_alloc();
void Move_init(Move* m, int length);
void Move_destroy(Move* m);

/* void printState(Board* b); */
char* Board_to_string(Board* b);
char* Move_to_string(Move* m);
// rather just access the struct from python and print it from there

void player(Board* b, char* str);
/* void actions(char* moves); */
Move** actions(Board* b, int* length);

Board* result(Board* b, Move* m);

#endif
