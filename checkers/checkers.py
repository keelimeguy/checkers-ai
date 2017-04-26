from checkers.state.bitboard_32_state import Bitboard32State
from checkers.sam_server import SamServer
from checkers.c.structs import *

class Checkers:

    class CheckersState:
        def __init__(self, player=None, board=None):
            self.player = player
            self.board = board
            if not self.board:
                self.board = Bitboard32State()

        def terminal(self):
            return self.board.count_foes() == 0 or self.board.count_friends() == 0

        def result(self, move=None):
            return Checkers().CheckersState(self.player, self.board.result(move))

        def actions(self):
            return self.board.actions()

        def list_actions(self):
            return self.board.list_actions()

    def __init__(self, opponent=0, is_B_client=False):
        self.gameState = self.CheckersState()
        self.server = SamServer(opponent, is_B_client)
        self.gameover = True
        self.moves = []

    def reset(self, verbose=False):
        self.server.disconnect()
        self.gameState = self.CheckersState(self.server.connect(verbose))
        self.moves = []
        if self.gameState.player:
            self.tell_server("")
        self.gameover = False

    def finished(self):
        return self.gameover

    def list_actions(self):
        return self.gameState.list_actions()

    def actions(self):
        return self.gameState.actions()

    def result(self, move=None):
        return self.gameState.result(move)

    def play(self, move=None):
        if move:
            self.moves.append(move)
            self.gameState.board = self.gameState.board.result(move)
            # returns False if error occurred, else True
            return self.tell_server(str(move))
        else:
            self.show_game()
            print("Null move error!")
            return True

    def tell_server(self, move=""):
        response = self.server.send_and_receive(move)
        if response:
            if "Result" in response:
                self.gameover = True
                self.server.disconnect()
                return False
            if "Error" in response:
                self.gameover = True
                self.server.disconnect()
                self.show_game()
                print("Error detected:")
                print(response)
                return True
            nextmove = self.gameState.board.move_from_string(response)
            self.moves.append(nextmove)
            self.gameState.board = self.gameState.board.result(nextmove)
        else:
            self.gameover = True
            self.server.disconnect()
            self.show_game()
            print("Unknown Error!")
            return True
        return False

    # We store a list of moves played throughout a game, and use this function to show the entire game at the end
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
        result = state.c_board.contents
        final = "\nUNKNOWN\n"
        if self.gameState.player and result.b or not self.gameState.player and result.w:
            extra_move = next(state.actions(), None)
            if extra_move:
                state = state.result(extra_move)
                result = state.c_board.contents
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
        return final.strip()
