#!/usr/bin/env python3

from bitboard_32_state import Bitboard32State
from sam_server import SamServer
from structs import *

from random import randint

moves = []

board = Bitboard32State()
server = SamServer()
player = server.connect()
if player:
    response = server.send_and_receive("")
    if response:
        nextmove = board.move_from_string(response)
        moves.append(nextmove)
        board = board.result(nextmove)
    else:
        print('------ERROR------')
        server.disconnect()

while server.connected:
    actions = board.list_actions()
    if len(actions)>1:
        index = randint(0, len(actions)-1)
    else:
        index = 0
    mymove = actions[index]

    moves.append(mymove)
    board = board.result(mymove)

    response = server.send_and_receive(str(mymove))
    if response:
        nextmove = board.move_from_string(response)
        moves.append(nextmove)
        board = board.result(nextmove)
    else:
        print('------ERROR------')
        server.disconnect()

print('\nRESULTS:')
for move in moves:
    print(move)
result = cast(board.board, POINTER(BOARD))
if player and result.contents.b or not player and result.contents.w:
    board = board.result(next(board.actions()))
    result = cast(board.board, POINTER(BOARD))
    if not player and result.contents.b or player and result.contents.w:
        print("DRAW!\n")
    else:
        print("LOST!\n")
else:
    print("WON!\n")
