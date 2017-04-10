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
void Board_init(Board* b, unsigned int _b, unsigned int _w, unsigned int _k, unsigned short _plyr);
void Board_destroy(Board* b);

Move* Move_alloc();
void Move_init(Move* m, int length);
void Move_destroy(Move* m);

// rather just access the struct from python and print it from there
/* void printState(Board* b); */

char Board_char_at_pos(Board* b, unsigned short pos);
char* Board_to_string(Board* b);
char* Move_to_string(Move* m);
unsigned short pos_to_row(unsigned short pos);
unsigned short pos_to_col(unsigned short pos);

void player(Board* b, char* str);
Move** actions(Board* b, int* length);
Board* result(Board* b, Move* m);

#endif
