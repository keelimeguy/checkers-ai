#! /bin/python

from structs import *

myboard = pointer(BOARD())
gameState32.Board_init(myboard, 0x00e06021, 0x00000200, 0x00000200, 1)

printf(gameState32.Board_to_string(myboard))
movelist = pointer(pointer(MOVE()))
numMoves = c_int(0)
movelist = gameState32.actions(myboard, byref(numMoves))
myboard = gameState32.result(myboard, movelist[numMoves.value-1])
printf(b"Make move: %s\n", gameState32.Move_to_string(movelist[numMoves.value-1]))
printf(gameState32.Board_to_string(myboard))
