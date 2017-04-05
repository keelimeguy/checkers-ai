/*------------------------------------------------------
   Keelin Becker-Wheeler
   CSE4705 - HW4: Checkers Representations
   "32-array" Representation - using 3 unsigned ints
------------------------------------------------------*/

#include "keelin_board.h"
#include "test_keelin.h"

// An unsigned int is 32-bits
// ( Notice that three unsigned ints is equivalent to a 32 length array of 3-bit variables,
//   hence the algorithms in this code will be equivalent to using a 32-b/* it array ) */
/* unsigned int w_board, b_board, k_board; // white, black, and king-ed pieces */
/* unsigned int curPlayer; */


/* void setup(unsigned int b, unsigned int w, unsigned int k, unsigned short plyr) { */
/*     b_board = b; */
/*     w_board = w; */
/*     k_board = k; */
/*     curPlayer = plyr; */
/* } */

Board* Board_alloc() {
  return malloc(sizeof(Board));
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

char Board_char_at_pos(Board* b, unsigned short pos) {
  char ret = '-';
  if (b->b & (1<<(pos-1)))
    ret = 'b';
  else if (b->w & (1<<(pos-1)))
    ret = 'w';
  if (b->k & (1<<(pos-1)))
    ret += ' '; // capitalize
  return ret;
}

char* Board_to_string(Board* b) {
  char* repr = malloc(86 * sizeof(char));
  int next = 0;
  for(int i = 1; i <= 32; i++) {
    if ((i-1) % 8 < 4) {
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
  player(b, & repr[next]);
  strcpy("'s move", & repr[next+5]);
  return repr;
}

/* char* Move_to_string(Move* m) { */
unsigned short pos_to_row(unsigned short pos) {
  return 7 - (pos - 1) / 4;
}
unsigned short pos_to_col(unsigned short pos) {
  return 2 * ((pos - 1) % 4) + (pos_to_row(pos) % 2);
}


void player(Board* b, char* str) {
    if (b->plyr)
        sprintf(str, "White");
    else
        sprintf(str, "Black");
}


Move* actions(Board* b) {
    if (b->plyr)
      // TODO fix move representation
        white_moves(moves, b->b, b->w, b->k, 0, (unsigned int*){0}, (unsigned int*){0});
    else
        black_moves(moves, b->b, b->w, b->k, 0, (unsigned int*){0}, (unsigned int*){0});
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
  unsigned short row_is_even = ! (pos_to_row(route[0]) % 2);
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
    }
  }

}
