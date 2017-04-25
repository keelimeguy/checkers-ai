#!/usr/bin/env python3

from checkers.state.bitboard_32_state import Bitboard32State
from checkers.sam_server import SamServer
from checkers.c.structs import *

class McCartneyServerPlayer:

    def __init__(self, opponent=0, is_B_client=False, verbose=False):
        """Pass
                opponent= SERVER_NUMBER
                is_B_client = ... If you want client #6 instead of #5
                verbose = if you want to hear the server complain
        """
        self.board = Bitboard32State()
        self.server = SamServer(opponent, is_B_client)

        self.am_white = self.server.connect(verbose)  # 1 if white else 0
        self.moves = []
        if self.am_white:
            self.tell_server("")
        self.gameover = False

    def recv_move(self, move):
        self.moves.append(move)
        self.board = self.board.result(move)
        # returns something based on whether error occurred
        self.tell_server(str(move))


    # TODO make this not block -- or we will super lose ;X
    def tell_server(self, move):
        response = self.server.send_and_receive(move)
        if response:
            if "Result" in response:
                self.server.disconnect()
                if "Result:Black" in response:
                    raise GameOver(result="Black")
                elif "Result:White" in response:
                    raise GameOver(result="White")
                else:
                    raise GameOver(result="Draw")
                    
            elif "Error" in response:
                self.server.disconnect()
                self.show_game()
                print("Error detected:")
                print(response)
                return True
            nextmove = self.board.move_from_string(response)
            self.moves.append(nextmove)
            self.board = self.board.result(nextmove)
        else:
            self.gameover = True
            self.server.disconnect()
            self.show_game()
            print("Unknown Error!")
            return True
        return False

    # We store a list of moves played throughout a game, and use this function to show the entire game at the end
    def show_game(self):
        """If ya feel like running this after the game, go ahead"""
        state = Bitboard32State()
        if self.am_white:
            print('Playing as White:\n')
        else:
            print('Playing as Black:\n')
        print(state)
        for move in self.moves:
            state = state.result(move)
            print(state)
        result = state.c_board.contents
        final = "\nUNKNOWN\n"
        if self.am_white and result.b or not self.am_white and result.w:
            extra_move = next(state.actions(), None)
            if extra_move:
                state = state.result(extra_move)
                result = state.c_board.contents
                if (not self.am_white and result.b
                    and state.actions() or self.am_white
                    and result.w and state.actions()):
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
