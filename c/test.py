#!/usr/bin/env python3

from structs import *

myboard = pointer(BOARD())
state32_lib.Board_init(myboard, 0x00e06021, 0x00000200, 0x00000200, 1)

printf(state32_lib.Board_to_string(myboard))
movelist = pointer(pointer(MOVE()))
numMoves = c_int(0)
movelist = state32_lib.actions(myboard, byref(numMoves))
printf(b"\n\nMake move: %s\n\n", state32_lib.Move_to_string(movelist[numMoves.value-1]))
myboard = state32_lib.result(myboard, movelist[numMoves.value-1])
printf(state32_lib.Board_to_string(myboard))

state32_lib.Move_list_destroy(movelist, numMoves)
movelist = state32_lib.actions(myboard, byref(numMoves))
printf(b"\n\nMake move: %s\n\n", state32_lib.Move_to_string(movelist[numMoves.value-1]))
myboard = state32_lib.result(myboard, movelist[numMoves.value-1])
printf(state32_lib.Board_to_string(myboard))

state32_lib.Move_list_destroy(movelist, numMoves)
movelist = state32_lib.actions(myboard, byref(numMoves))
printf(b"\n\nMake move: %s\n\n", state32_lib.Move_to_string(movelist[numMoves.value-1]))
myboard = state32_lib.result(myboard, movelist[numMoves.value-1])
printf(state32_lib.Board_to_string(myboard))

state32_lib.Move_list_destroy(movelist, numMoves)
movelist = state32_lib.actions(myboard, byref(numMoves))
printf(b"\n\nMake move: %s\n\n", state32_lib.Move_to_string(movelist[numMoves.value-1]))
myboard = state32_lib.result(myboard, movelist[numMoves.value-1])
printf(state32_lib.Board_to_string(myboard))
printf(b"\n")

state32_lib.Move_list_destroy(movelist, numMoves)
state32_lib.Board_destroy(myboard)
