/*------------------------------------------------------
     Keelin Becker-Wheeler
     CSE4705 - HW4: Checkers Representations
     "32-array" Representation - using 3 unsigned ints
------------------------------------------------------*/

#include "checkers32.h"

Board* Board_alloc() {
    return malloc(sizeof(Board));
}

void Board_init(Board* b, unsigned int _b, unsigned int _w, unsigned int _k, unsigned short _plyr) {
    b->b = _b;
    b->w = _w;
    b->k = _k;
    b->plyr = _plyr;
}

void Board_destroy(Board* b) {
    free(b);
}

Move* Move_alloc() {
    return malloc(sizeof(Move));
}

void Move_init(Move* m, int length) {
    m->length = length;
    m->route = malloc(length * sizeof(unsigned short));
}

void Move_destroy(Move* m) {
    free(m->route);
    free(m);
}

void Move_list_destroy(Move** m, int size) {
    for (int i = 0; i < size; i++)
        Move_destroy(m[i]);
    free(m);
}

char Board_char_at_pos(Board* b, unsigned short pos) {
    char ret = '-';
    if (b->b & (1<<(pos-1)))
        ret = 'b';
    else if (b->w & (1<<(pos-1)))
        ret = 'w';
    if (b->k & (1<<(pos-1)))
        ret -= ' '; // capitalize
    return ret;
}

char* Board_to_string(Board* b) {
    char* repr = malloc(85 * sizeof(char));
    int next = 0;
    for(int i = 1; i <= 32; i++) {
        if (pos_to_row(i)%2) {
            repr[next++] = '+';
            repr[next++] = Board_char_at_pos(b, i);
        } else {
            repr[next++] = Board_char_at_pos(b, i);
            repr[next++] = '+';
        }
        if (i % 4 == 0) {
            repr[next++] = '\n';
        }
    }
    repr[next++] = '\n';
    char* playerStr = player(b);
    for (int i = 0; i < 5; i++)
        repr[next+i] = playerStr[i];
    repr[next+5]='\'';
    repr[next+6]='s';
    repr[next+7]=' ';
    repr[next+8]='m';
    repr[next+9]='o';
    repr[next+10]='v';
    repr[next+11]='e';
    repr[next+12]='\0';
    return repr;
}

Board* Board_from_string(char* str) {
    if (strlen(str)!=85) return (Board*){0};
    Board* ret = Board_alloc();
    int next = 0;
    unsigned int b = 0, w = 0, k = 0;
    for(int i = 1; i <= 32; i++) {
        if (pos_to_row(i)%2)
            next++;
        if (str[next]=='B') {
            b |= (1<<(i-1));
            k |= (1<<(i-1));
        } else if (str[next]=='W') {
            w |= (1<<(i-1));
            k |= (1<<(i-1));
        } else if (str[next]=='b') {
            b |= (1<<(i-1));
        } else if (str[next]=='w') {
            w |= (1<<(i-1));
        }
        next++;
        if (!(pos_to_row(i)%2))
            next++;
        if (i % 4 == 0)
            next++;
    }
    next++;
    if (str[next]=='W') ret->plyr = 1;
    else ret->plyr = 0;
    ret->b = b;
    ret->w = w;
    ret->k = k;
    return ret;
}

char* Move_to_string(Move* m) {
    char* repr = malloc((m->length*5 + m->length) * sizeof(char));
    for (int i = 0; i < m->length; i++) {
        unsigned short pos = m->route[i];
        repr[i*6] = '(';
        repr[i*6+1] = (char)(pos_to_row(pos) + 48);
        repr[i*6+2] = ':';
        repr[i*6+3] = (char)(pos_to_col(pos) + 48);
        repr[i*6+4] = ')';
        if (i != m->length-1)
            repr[i*6+5] = ':';
        else repr[i*6+5] = (char)0;
    }
    return repr;
}

Move* Move_from_string(char* str) {
    unsigned int len = strlen(str);
    if (str==0 || len<11) return (Move*){0};

    unsigned short row_start = (unsigned short)(str[1]-48); // 48 is ASCII for '0'
    unsigned short col_start = (unsigned short)(str[3]-48);
    unsigned short row_end = row_start;
    unsigned short col_end = col_start;

    int numSteps = 1;
    unsigned short temp_pos[10]; // Max move should be 9 jumps.. I think
    temp_pos[0] = (7-row_start)*4+1 + col_start/2;

    int index = 5;
    while (index<len && str[index]==':') {
        index+=2;

        row_start = row_end;
        col_start = col_end;

        row_end = (unsigned short)(str[index]-48);
        index+=2;
        col_end = (unsigned short)(str[index]-48);
        index+=2;

        temp_pos[numSteps++] = (7-row_end)*4+1 + col_end/2;
    }

    Move* ret = Move_alloc();
    Move_init(ret, numSteps);
    for (int j = 0; j<numSteps; j++)
        ret->route[j] = temp_pos[j];
    return ret;
}


char* player(Board* b) {
    char* str = malloc(6*sizeof(char));
    if (b->plyr)
        sprintf(str, "White");
    else
        sprintf(str, "Black");
    str[5] = (char)0;
    return str;
}

Move** actions(Board* b, int* length) {
    char moveStr[999]; // Sorry...
    moveStr[0] = 0; // Just in case...

    if (b->plyr)
        white_moves(moveStr, b->b, b->w, b->k);
    else
        black_moves(moveStr, b->b, b->w, b->k);

    // Convert string of moves into Move list..

    int len = strlen(moveStr);
    int numMoves = 0;
    if (len > 10) numMoves = 1;
    for (int i = 0; i < len; i++)
        if(moveStr[i] == ',') numMoves++;
    *length = numMoves;

    if (numMoves==0) return (Move**){0};

    // Allocate space for move list
    Move** ret = malloc(sizeof(Move)*numMoves);

    int index = 0;
    for (int i = 0; i < numMoves; i++) {
        unsigned short row_start = (unsigned short)(moveStr[index+1]-48); // 48 is ASCII for '0'
        unsigned short col_start = (unsigned short)(moveStr[index+3]-48);
        unsigned short row_end = row_start;
        unsigned short col_end = col_start;

        // (r:c):(r:c):(r:c), (r:c):(r:C)

        int numSteps = 1;
        unsigned short temp_pos[10]; // Max move should be 9 jumps.. I think
        temp_pos[0] = (7-row_start)*4+1 + col_start/2;

        index+=5;
        while (index<len && moveStr[index]!=',') {
            index+=2;

            row_start = row_end;
            col_start = col_end;

            row_end = (unsigned short)(moveStr[index]-48);
            index+=2;
            col_end = (unsigned short)(moveStr[index]-48);
            index+=2;

            temp_pos[numSteps++] = (7-row_end)*4+1 + col_end/2;
        }
        index+=2;

        ret[i] = Move_alloc();
        Move_init(ret[i], numSteps);
        for (int j = 0; j<numSteps; j++)
            ret[i]->route[j] = temp_pos[j];
    }
    return ret;
}

Board* result(Board* b, Move* move) {
    Board* res = Board_alloc();
    res->b = b->b;
    res->w = b->w;
    res->k = b->k;
    res->plyr = ! b->plyr;

    int index = 0;
    unsigned short pos_start;
    unsigned short pos_end;
    unsigned short row_is_even = ! (pos_to_row(move->route[0]) % 2);
    while(index < (move->length - 1)) {

        pos_start = move->route[index++];
        pos_end = move->route[index];

        if(b->plyr) {
            res->w &= ~(1<<(pos_start-1));
            if (pos_start-pos_end>6 || pos_start-pos_end<6) { // Jumped a piece
                if (pos_start-pos_end == -7) {
                    if (row_is_even) {
                        res->b &= ~(1<<(pos_start+2)); // +3 (-1)
                        res->k &= ~(1<<(pos_start+2)); // +3 (-1)
                    } else {     // If started on odd row
                        res->b &= ~(1<<(pos_start+3)); // +4 (-1)
                        res->k &= ~(1<<(pos_start+3)); // +4 (-1)
                    }
                } else if (pos_start-pos_end == -9) {
                    if (row_is_even) {
                        res->b &= ~(1<<(pos_start+3)); // +4 (-1)
                        res->k &= ~(1<<(pos_start+3)); // +4 (-1)
                    } else {     // If started on odd row
                        res->b &= ~(1<<(pos_start+4)); // +5 (-1)
                        res->k &= ~(1<<(pos_start+4)); // +5 (-1)
                    }
                } else if (pos_start-pos_end == 7) {
                    if (row_is_even) {
                        res->b &= ~(1<<(pos_start-5)); // -4 (-1)
                        res->k &= ~(1<<(pos_start-5)); // -4 (-1)
                    } else {     // If started on odd row
                        res->b &= ~(1<<(pos_start-4)); // -3 (-1)
                        res->k &= ~(1<<(pos_start-4)); // -3 (-1)
                    }
                } else if (pos_start-pos_end == 9) {
                    if (row_is_even) {
                        res->b &= ~(1<<(pos_start-6)); // -5 (-1)
                        res->k &= ~(1<<(pos_start-6)); // -5 (-1)
                    } else {     // If started on odd row
                        res->b &= ~(1<<(pos_start-5)); // -4 (-1)
                        res->k &= ~(1<<(pos_start-5)); // -4 (-1)
                    }
                }
            }
            res->w |= (1<<(pos_end-1));
            if(res->k &(1<<(pos_start-1))) {
                res->k &= ~(1<<(pos_start-1));
                res->k |= (1<<(pos_end-1));
            }
            if(pos_to_row(pos_end) == 7) // King the piece!
                res->k |= (1<<(pos_end-1));
        } else {
            res->b &= ~(1<<(pos_start-1));
            if (pos_start-pos_end>6 || pos_start-pos_end<6) { // Jumped a piece
                if (pos_start-pos_end ==  -7) {
                    if (row_is_even) {
                        res->w &= ~(1<<(pos_start+2)); // +3 (-1)
                        res->k &= ~(1<<(pos_start+2)); // +3 (-1)
                    } else {     // If started on odd row
                        res->w &= ~(1<<(pos_start+3)); // +4 (-1)
                        res->k &= ~(1<<(pos_start+3)); // +4 (-1)
                    }
                } else if (pos_start-pos_end ==  -9) {
                    if (row_is_even) {
                        res->w &= ~(1<<(pos_start+3)); // +4 (-1)
                        res->k &= ~(1<<(pos_start+3)); // +4 (-1)
                    } else {     // If started on odd row
                        res->w &= ~(1<<(pos_start+4)); // +5 (-1)
                        res->k &= ~(1<<(pos_start+4)); // +5 (-1)
                    }
                } else if (pos_start-pos_end ==  7) {
                    if (row_is_even) {
                        res->w &= ~(1<<(pos_start-5)); // -4 (-1)
                        res->k &= ~(1<<(pos_start-5)); // -4 (-1)
                    } else {     // If started on odd row
                        res->w &= ~(1<<(pos_start-4)); // -3 (-1)
                        res->k &= ~(1<<(pos_start-4)); // -3 (-1)
                    }
                } else if (pos_start-pos_end ==  9) {
                    if (row_is_even) {
                        res->w &= ~(1<<(pos_start-6)); // -5 (-1)
                        res->k &= ~(1<<(pos_start-6)); // -5 (-1)
                    } else {     // If started on odd row
                        res->w &= ~(1<<(pos_start-5)); // -4 (-1)
                        res->k &= ~(1<<(pos_start-5)); // -4 (-1)
                    }
                }
            }
            res->b |= (1<<(pos_end-1));
            if(res->k &(1<<(pos_start-1))) {
                res->k &= ~(1<<(pos_start-1));
                res->k |= (1<<(pos_end-1));
            }
            if(pos_to_row(pos_end) == 0) // King the piece!
                res->k |= (1<<(pos_end-1));
        }
    }
    return res;
}
