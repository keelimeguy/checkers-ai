#!/usr/bin/env python3

from threading import Thread
import queue

import sys

from checkers.state import Bitboard32State
from checkers.sam_server import SamServer
# from checkers.heuristics import BoardEvaluator

from checkers.game_api import GameOver, CheckersServerBase

class McCartneyServerPlayer(Thread, CheckersServerBase):

    def __init__(self, opponent=0, is_B_client=False, verbose=False):
        """Pass
                opponent= SERVER_NUMBER
                is_B_client = ... If you want client #6 instead of #5
                verbose = if you want to hear the server complain
        """
        super().__init__()
        self.board = Bitboard32State()
        self.server = SamServer(opponent, is_B_client)

        self.client_is_white = self.server.connect(verbose)  # 1 if white else 0
        self.moves = []
        self.queue_to_send = queue.Queue(1)  # moves to send to the server
        self.queue_replies = queue.Queue(1)  # moves the server sends to us

        if self.client_is_white:
            self._tell_server("")
        self.gameover = False

    def recv_move(self, move):
        self.moves.append(move)  # not thread safe, but okay for correct use
        self.board = self.board.result(move)
        # The sequence
        #   get a move from server (and enqueue)
        #   dequeue that move (and feed to client player)
        #   recv a move from the client player
        # should never be broken.  (Unless we pipeline our messages for
        # sequences of forced jumps, but that would fail unless the other team
        # did the same optimization! Please don't do that!)
        # Thus this exception:
        if self.queue_replies.qsize() != 0:
            raise RuntimeError(  # see note above before commenting this out
                f"recv_move ({str(move)}) called on a {type(self)} with "
                "nonzero pending messages from server")

        return self._tell_server(str(move))
        # self.queue_to_send.put(str(move), block=False)

    def make_move(self):
        """Make a move (blocking)"""
        result = self.queue_replies.get(block=True)
        if isinstance(result, GameOver):
            raise result
        else:
            return result

    def going_first(self):
        return self.client_is_white

    def run(self):
        # This what runs in the thread
        while True:
            self.queue_replies.put(
                self._tell_server(self.queue_to_send.get(block=True)),
                block=False)  # raise exception if queue is full

    def _tell_server(self, move):
        """tell the server the move and block while waiting for response"""
        response = self.server.send_and_receive(move)
        if response:
            if "Result" in response:
                self.server.disconnect()
                if "Result:Black" in response:
                    return GameOver(result="Black")
                elif "Result:White" in response:
                    return GameOver(result="White")
                else:
                    return GameOver(result="Draw")

            elif "Error" in response:
                self.server.disconnect()
                self.show_game()
                print("Error detected:", file=sys.stderr)
                print(response, file=sys.stderr)
                return GameOver(result=None)
            nextmove = self.board.Move.from_string(response)
            self.moves.append(nextmove)
            self.board = self.board.result(nextmove)
        else:
            self.gameover = True
            self.server.disconnect()
            self.show_game()
            print("Unknown Error: No Response", file=sys.stderr)
            return GameOver(result=None)


    # We store a list of moves played throughout a game, and use this function to show the entire game at the end
    def show_game(self):
        """If ya feel like running this after the game, go ahead

        It reports a draw even if somebody won based on a timeout"""
        state = Bitboard32State()
        if self.client_is_white:
            print('Playing as White:\n')
        else:
            print('Playing as Black:\n')
        print(state)
        for move in self.moves:
            state = state.result(move)
            print(state)
        result = state.c_board.contents
        final = "\nUNKNOWN\n"
        if (self.client_is_white and result.b
                or not self.client_is_white and result.w):
            extra_move = next(state.actions(), None)
            if extra_move:
                state = state.result(extra_move)
                result = state.c_board.contents
                if (not self.client_is_white and result.b
                    and state.actions() or self.client_is_white
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


# class MinMaxClientPlayer(Thread, CheckersClientBase):

#     def __init__(self, state=None, weights=None):
#         """You'd better pass in a dictionary of weights"""
#         super().__init__()
#         # self.evaluate = evaluation_function  # better make a subclass instead
#         self.state = BitBoard32State()
#         self.inbox = queue.Queue(1)
#         self.search_engine = AlphaBeta(
#         self.go_first_q = queue.Queue(1)
#         self.outbox = queue.Queue(1)
#         # going_first = None  # None if unset, False later
#         self._responses = {}  # dict of move -> move

#     def set_going_first(self, go_first):
#         """Must be called to tell the player whether to go first"""
#         self.go_first_q.put(go_first, block=False)

#     def recv_move(self, move):
#         self.inbox.put(move,
#                        block=False)  # useful error if queue is Full


#     def run(self):
#         # wait to be told who is going first
#         go_first = self.go_first_q.get(block=True)

#         if go_first:
            
#         while True:
#             self.outbox.put(
