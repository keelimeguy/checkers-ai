#! /bin/python

from structs import *

myboard = BOARD()
myboard.b = 0x00e06021
myboard.w = 0x00000200
myboard.k = 0x00000200
myboard.plyr = 1

gameState32.print_board(myboard)
movelist = POINTER(MOVE())
movelist = gameState32.actions(myboard)
myboard = gameState32.result(myboard, movelist[0])
gameState32.print_board(myboard)
