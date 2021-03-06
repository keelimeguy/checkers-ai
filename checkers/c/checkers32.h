#ifndef CHECKERS32_H
#define CHECKERS32_H

#include "checkers32_calc.h"

typedef struct Board {
    unsigned int b, w, k;
    unsigned short plyr;
} Board;

typedef struct Move {
    unsigned short* route;
    unsigned int length;
} Move;

Board* Board_alloc(void);
void Board_init(Board* b, unsigned int _b, unsigned int _w, unsigned int _k, unsigned short _plyr);
void Board_destroy(Board* b);

Move* Move_alloc(void);
void Move_init(Move* m, unsigned int length);
Move* Move_copy(Move* src);
void Move_list_destroy(Move** m, unsigned int size);
void Move_destroy(Move* m);

char Board_char_at_pos(Board* b, unsigned int pos);
char* Board_to_string(Board* b);
Board* Board_from_string(char* str);
char* Move_to_string(Move* m);
Move* Move_from_string(char* str);

char* player(Board* b);
Move** actions(Board* b, unsigned int* length);
Board* result(Board* b, Move* m);

#endif
