#! /bin/python

from structs import *

myboard = pointer(BOARD())
state32.Board_init(myboard, 0x00e06021, 0x00000200, 0x00000200, 1)

printf(state32.Board_to_string(myboard))
movelist = pointer(pointer(MOVE()))
numMoves = c_int(0)
movelist = state32.actions(myboard, byref(numMoves))
printf(b"\n\nMake move: %s\n\n", state32.Move_to_string(movelist[numMoves.value-1]))
myboard = state32.result(myboard, movelist[numMoves.value-1])
printf(state32.Board_to_string(myboard))

state32.Move_list_destroy(movelist, numMoves)
movelist = state32.actions(myboard, byref(numMoves))
printf(b"\n\nMake move: %s\n\n", state32.Move_to_string(movelist[numMoves.value-1]))
myboard = state32.result(myboard, movelist[numMoves.value-1])
printf(state32.Board_to_string(myboard))

state32.Move_list_destroy(movelist, numMoves)
movelist = state32.actions(myboard, byref(numMoves))
printf(b"\n\nMake move: %s\n\n", state32.Move_to_string(movelist[numMoves.value-1]))
myboard = state32.result(myboard, movelist[numMoves.value-1])
printf(state32.Board_to_string(myboard))

state32.Move_list_destroy(movelist, numMoves)
movelist = state32.actions(myboard, byref(numMoves))
printf(b"\n\nMake move: %s\n\n", state32.Move_to_string(movelist[numMoves.value-1]))
myboard = state32.result(myboard, movelist[numMoves.value-1])
printf(state32.Board_to_string(myboard))
printf(b"\n")

state32.Move_list_destroy(movelist, numMoves)
state32.Board_destroy(myboard)
