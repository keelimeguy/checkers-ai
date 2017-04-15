#!/usr/bin/env python3

from bitboard_32_state import Bitboard32State
from sam_server import SamServer

from random import randint

moves = []

board = Bitboard32State()
server = SamServer()

if server.connect(True):
    response = server.send_and_receive("")
    if response:
        nextmove = board.move_from_string(response)
        moves.append(nextmove)
        board = board.result(nextmove)
    else:
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
        server.disconnect()

print('\nRESULT')
for move in moves:
    print(move)
