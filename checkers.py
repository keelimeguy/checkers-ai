from bitboard_32_state import Bitboard32State
from sam_server import SamServer
from structs import *

import random
import time

class Checkers:

    class CheckersState:
        def __init__(self, player=None, board=Bitboard32State()):
            self.player = player
            self.board = board

        def terminal(self):
            return self.board.count_foes() == 0 or self.board.count_friends() == 0

        def result(self, move=None):
            return Checkers().CheckersState(self.player, self.board.result(move))

        def actions(self):
            return self.board.actions()

        def eval(self, move=None):
            state = self.board.result(move)
            score = state.count_friends() - state.count_foes() + 3*state.count_crowned_friends() - 3*state.count_crowned_foes()
            if state.board.contents.plyr == self.player:
                return score
            return -score


    def __init__(self):
        self.gameState = self.CheckersState()
        # self.server = SamServer()
        # self.server = SamServer(6)
        self.server = SamServer(5, True)
        self.gameover = True
        self.moves = []

    def reset(self, verbose=False):
        random.seed(time.time())
        self.server.disconnect()
        self.gameState = self.CheckersState(self.server.connect(verbose))
        self.moves = []
        if self.gameState.player:
            self.tell_server("")
        self.gameover = False

    def finished(self):
        return self.gameover

    def actions(self):
        return self.gameState.actions()

    def result(self, move=None):
        return self.CheckersState(self.gameState.player, self.gameState.board.result(move))

    def play(self, move=None):
        if move:
            self.moves.append(move)
            self.gameState.board = self.gameState.board.result(move)
            self.tell_server(str(move))

    def tell_server(self, move=""):
        response = self.server.send_and_receive(move)
        if response:
            nextmove = self.gameState.board.move_from_string(response)
            self.moves.append(nextmove)
            self.gameState.board = self.gameState.board.result(nextmove)
        else:
            self.gameover = True
            self.server.disconnect()

    def show_game(self):
        state = Bitboard32State()
        if self.gameState.player:
            print('Playing as White:\n')
        else:
            print('Playing as Black:\n')
        print(state)
        for move in self.moves:
            state = state.result(move)
            print(state)
        result = state.board.contents
        final = "\nUNKNOWN\n"
        if self.gameState.player and result.b or not self.gameState.player and result.w:
            actions = state.actions()
            if actions:
                extra_move = next(actions)
                state = state.result(extra_move)
                result = state.board.contents
                if not self.gameState.player and result.b and state.actions() or self.gameState.player and result.w and state.actions():
                    final = "\nDRAW!\n"
                else:
                    self.moves.append(extra_move)
                    print(state)
                    final = "\nLOST!\n"
            else:
                final = "\nDRAW!\n"
        else:
            final = "\nWON!\n"
        for move in self.moves:
            print(move)
        print(final)

def alphabeta(node, depth = 7, alpha=float('-inf'), beta=float('inf'), maximum=True):
    if depth == 0 or node.terminal():
        return node.eval()
    if maximum:
        val = float('-inf')
        actions = node.actions()
        action = next(actions, None)
        while action:
            child = node.result(action)
            val = max(val, alphabeta(child, depth - 1, alpha, beta, False))
            alpha = max(alpha, val)
            if beta <= alpha:
                break
            action = next(actions, None)
        return val
    else:
        val = float('inf')
        actions = node.actions()
        action = next(actions, None)
        while action:
            child = node.result(action)
            val = min(val, alphabeta(child, depth - 1, alpha, beta, True))
            beta = min(beta, val)
            if beta <= alpha:
                break
            action = next(actions, None)
        return val

if __name__ == "__main__":
    game = Checkers()
    game.reset(True)
    while not game.finished():
        move = None
        actions = game.actions()
        action = next(actions, None)
        bestScore = float('-inf')
        while action:
            score = alphabeta(game.result(action))
            # print(game.gameState.board.result(action), '\nhas score: ', score)
            if float(score) > bestScore:
                bestScore = score
                move_list = [action]
            elif score == bestScore:
                move_list.append(action)
            action = next(actions, None)
        index = random.randint(0, len(move_list)-1)
        game.play(move_list[index])
    game.show_game()
