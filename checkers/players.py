#!/usr/bin/env python3

from threading import Thread
import queue
from math import inf

import sys

from checkers.state import Bitboard32State
from checkers.sam_server import SamServer
from checkers.heuristics import BoardEvaluator
from checkers.alphabeta import AlphaBeta


from checkers.game_api import GameOver, CheckersServerBase, CheckersClientBase

class McCartneyServerPlayer(Thread, CheckersServerBase):

    def __init__(self, opponent=0, is_B_client=False, verbose=False):
        """Pass
                opponent= SERVER_NUMBER
                is_B_client = ... If you want client #6 instead of #5
                verbose = if you want to hear the server complain
        """
        super().__init__()
        self._server_verbose = verbose
        self.board = Bitboard32State()
        self.server = SamServer(opponent, is_B_client)

        self._client_is_white = None
        self._client_is_white_q = queue.Queue(1)
        self.moves = []
        self.queue_to_send = queue.Queue(1)  # moves to send to the server
        self.queue_replies = queue.Queue(1)  # moves the server sends to us


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

        self.queue_to_send.put(str(move), block=False)

    def make_move(self):
        """Make a move (blocking)"""
        result = self.queue_replies.get(block=True)
        if isinstance(result, GameOver):
            raise result
        else:
            return result

    def going_first(self):
        if self._client_is_white is None:
            self._client_is_white = self._client_is_white_q.get(block=True)
        return self._client_is_white

    def run(self):
        # This what runs in the thread
        self._client_is_white_q.put(
            self.server.connect(verbose=self._server_verbose),
            block=False) # 1 if white else 0
        if self._client_is_white:
            self._tell_server("")

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
        if self._client_is_white:
            print('Playing as White:\n')
        else:
            print('Playing as Black:\n')
        print(state)
        for move in self.moves:
            state = state.result(move)
            print(state)
        result = state.c_board.contents
        final = "\nUNKNOWN\n"
        if (self._client_is_white and result.b
                or not self._client_is_white and result.w):
            extra_move = next(state.actions(), None)
            if extra_move:
                state = state.result(extra_move)
                result = state.c_board.contents
                if (not self._client_is_white and result.b
                    and state.actions() or self._client_is_white
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


class MinMaxClientPlayer(Thread, CheckersClientBase):

    class StopPrecomputation(Exception):
        """Thrown when we receive a move and need to stop precomputing"""

    def __init__(self, state=None, weights=None):
        """You'd better pass in a dictionary of weights"""
        super().__init__()
        # self.evaluate = evaluation_function  # better make a subclass instead
        self._state = Bitboard32State()
        self._inbox = queue.Queue(1)
        self._evaluator = BoardEvaluator(weights)
        self._search_engine = AlphaBeta(self._evaluator,
                                        default_depth=7)
        self._go_first_q = queue.Queue(1)
        self._outbox = queue.Queue(1)
        # going_first = None  # None if unset, False later
        self._responses = {}  # dict of move -> move

    def set_going_first(self, go_first):
        """Must be called to tell the player whether to go first"""
        self._go_first_q.put(go_first, block=False)

    def recv_move(self, move):
        self._inbox.put(move,
                        block=False)  # useful error if queue is Full

    def run(self):
        # wait to be told who is going first
        go_first = self._go_first_q.get(block=True)

        if go_first:
            move = self._choose_move()
            self._outbox.put(move)
            self._state = self._state.result(move)

        while True:
            try:
                self._precompute()
            except self.StopPrecomputation:
                pass
            # block if necessary because that would mean we finished
            # precomputation before our opponent made a move
            enemy_move = self._inbox.get(block=True)
            self._state = self._state.result(enemy_move)
            if enemy_move in self._responses:
                move = self._responses[enemy_move]
            else:
                move = self._choose_move()

            self._outbox.put(move, block=False)
            self._state = self._state.result(move)

    def _precompute(self):
        # modifies self._responses with snappy answers to moves we expected
        # this should only be called on the enemy's turn
        self._responses.clear()  # clear responses to old moves
        options = sorted(self._state.actions(),
                         key=(lambda board: - self._evaluator(board)))

        def check_inbox():
            if self._inbox.qsize() > 0:
                raise self.StopPrecomputation()

        for option in options:
            self._responses[option] = self._choose_move(
                self._state.result(option),
                side_effect=check_inbox)


                # while True:
        #     self.outbox.put(


    def _choose_move(self, state=None, **kwargs):
        """pick the next move"""
        if state is None:
            state = self._state

        alpha = -inf
        best_yet = None
        for act in sorted(state.actions(),
                          # lowest value for opponent first
                          key=(lambda a: self._evaluator(state.result(a)))):

            if best_yet is None:
                # almost redundant, but keeps us from stalling if we're losing
                best_yet = act

            current_val = self._search_engine.ab_dfs(
                state.result(act), alpha=alpha, maximum=False,
                **kwargs)
            if current_val > alpha:
                alpha = current_val
                best_yet = act
        return best_yet

class SimpleMcCartneyServerPlayer(McCartneyServerPlayer):
    def __init__(self, opponent=0, is_B_client=False, verbose=False):
        super().__init__(opponent, is_B_client, verbose)
        if self.client_is_white:
            self._tell_server("")

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

        # This version does not use the queue and threading, meant to directly make and recieve moves
        # ..hence "Simple"
        return self._tell_server(str(move))
        # self.queue_to_send.put(str(move), block=False)

