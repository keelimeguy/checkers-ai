#!/usr/bin/env python3

import queue
import sys
import random
import time

from threading import Thread, Event

try:
    from math import inf
except ImportError:
    inf = float('inf')

from checkers.state import Bitboard32State
from checkers.sam_server import SamServer
from checkers.heuristics import BoardEvaluator
from checkers.alphabeta import AlphaBeta

from checkers.game_api import GameOver, CheckersServerBase, CheckersClientBase

class McCartneyServerPlayer(Thread, CheckersServerBase):

    class StopThreadExecution(Exception):
        """Thrown when the server thread ought to stop completely"""

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
        print(str(self.board))
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
                "recv_move ({}) called on a {} with "
                "nonzero pending messages from server".format(str(move), type(self)))

        self.queue_to_send.put(str(move.copy()), block=False)

    def make_move(self):
        """Make a move (blocking)"""
        result = self.queue_replies.get(block=True)
        if isinstance(result, GameOver):
            self._tell_thread_to_stop()
            raise result
        return result

    def _tell_thread_to_stop(self):
        self.queue_to_send.put(self.StopThreadExecution())

    def going_first(self):
        # The server goes first if the client is white
        if self._client_is_white is None:
            self._client_is_white = self._client_is_white_q.get(block=True)
        return self._client_is_white

    def run(self):
        # This what runs in the thread
        self._client_is_white_q.put(
            self.server.connect(verbose=self._server_verbose),
            block=False) # 1 if white else 0
        time.sleep(0.001)

        if self.going_first():
            self.queue_replies.put(self._tell_server(""),block=False)

        try:
            while True:
                response = self._tell_server(self.queue_to_send.get(block=True))
                if not isinstance(response, GameOver):
                    response = response.copy()
                self.queue_replies.put(response,
                    block=False)  # raise exception if queue is full
        except self.StopThreadExecution:
            print("McCartneyServerPlayer finished running",file=sys.stderr)
            return

    def _tell_server(self, move):
        """tell the server the move and block while waiting for response"""

        if isinstance(move, self.StopThreadExecution):
            raise move

        response = self.server.send_and_receive(move)
        if response:
            if "Result" in response:
                self.server.disconnect()
                if "Result:Black" in response:
                    return GameOver(result="Black", client_win=((not self.going_first()) == 1))
                elif "Result:White" in response:
                    return GameOver(result="White", client_win=(self.going_first() == 1))
                else:
                    return GameOver(result="Draw", client_win=False)

            elif "Error" in response:
                self.server.disconnect()
                self.show_game()
                print("Error detected:", file=sys.stderr)
                print(response, file=sys.stderr)
                return GameOver(result=None, client_win=None)
            nextmove = self.board.Move.from_string(response)
            self.moves.append(nextmove)
            self.board = self.board.result(nextmove)
            return self.board.move_from_string(response)
        else:
            self.server.disconnect()
            self.show_game()
            print("Unknown Error: No Response", file=sys.stderr)
            return GameOver(result=None, client_win=None)


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

    class StopThreadExecution(Exception):
        """Thrown when the thread ought to stop completely"""

    def __init__(self, state=None, weights=None, evaluator=None, depth=7):
        """You'd better pass in a dictionary of weights

        evaluator takes precedence over weights"""

        super().__init__()
        # self.evaluate = evaluation_function  # better make a subclass instead
        self._state = Bitboard32State()
        self._inbox = queue.Queue(1)
        self._evaluator = evaluator or BoardEvaluator(weights)
        self._search_engine = AlphaBeta(self._evaluator,
                                        default_depth=depth)
        # self._search_engine.cache_quality_fudge = 2
        self._go_first_q = queue.Queue(1)
        self._outbox = queue.Queue(1)
        self._game_over_event = Event()
        # going_first = None  # None if unset, False later
        self._responses = {}  # dict of move -> move

    def set_going_first(self, go_first):
        """Must be called to tell the player whether to go first"""
        self._go_first_q.put(go_first, block=False)

    def recv_move(self, move):
        if isinstance(move, GameOver):
            self.tell_game_over()
        else:
            self._inbox.put(move.copy(),
                        block=False)  # useful error if queue is Full

    def tell_game_over(self):
        self._game_over_event.set()

    def run(self):
        # wait to be told who is going first
        go_first = self.safe_get_queue_blocking(self._go_first_q)

        if go_first:
            move = self._choose_move()
            self._outbox.put(move.copy(), block=False)
            interim  = self._state.result(move)
            self._state = interim
        try:
            while True:
                try:
                    self._precompute()
                except self.StopPrecomputation:
                    # print("stopped precomputing", file=sys.stderr)
                    pass
                # block if necessary because that would mean we finished
                # precomputation before our opponent made a move
                enemy_move = self.safe_get_queue_blocking(self._inbox).copy()
                self._state = self._state.result(enemy_move)
                if enemy_move in self._responses:
                    move = self._responses[enemy_move]
                else:
                    move = self._choose_move()
                self._outbox.put(move.copy(), block=False)
                self._state = self._state.result(move)
        except self.StopThreadExecution:
            print("{} ending!".format(self.name), file=sys.stderr)
            return

    def safe_get_queue_blocking(self, some_queue):
        while True:
            try:
                return some_queue.get(block=True, timeout=0.5)
            except queue.Empty:
                if self._game_over_event.is_set():
                    print("{} ending soon!".format(self.name), file=sys.stderr)
                    raise self.StopThreadExecution()

    def make_move(self):
        ret = self.safe_get_queue_blocking(self._outbox)
        return ret


    def _precompute(self):
        # modifies self._responses with snappy answers to moves we expected
        # this should only be called on the enemy's turn
        self._responses.clear()  # clear responses to old moves
        options = sorted(self._state.actions(),
                         key=(lambda move: -self._evaluator(self._state
                                                            .result(move))))

        def check_inbox():
            if self._inbox.qsize() > 0:
                raise self.StopPrecomputation()

        for option in options:
            self._responses[option] = self._choose_move(
                self._state.result(option),
                side_effect=check_inbox)


    def _choose_move(self, state=None, **kwargs):
        """pick the next move"""
        if state is None:
            state = self._state

        alpha = -inf
        best_yet = None
        if len(list(state.actions())) is 1:
            return next(state.actions())
        for act in sorted(state.actions(),
                          # lowest value for opponent first
                          key=(lambda a: self._evaluator(state.result(a)))):
            # print("Considering {}".format(str(act)), file=sys.stderr)
            if best_yet is None:
                # almost redundant, but keeps us from stalling if we're losing
                best_yet = [act]

            current_val = self._search_engine.ab_dfs(
                state.result(act), alpha=alpha, maximum=False,
                **kwargs)
            if current_val > alpha:
                alpha = current_val
                best_yet = [act]
            elif current_val == alpha:
                best_yet.append(act)
        index = random.randint(0, len(best_yet)-1) if best_yet is not None and len(best_yet)>1 else 0
        chosen = best_yet[index] if best_yet is not None else None
        # print("Chose a move {}".format(chosen))
        if not chosen:
            print(next(state.actions(), None), file=sys.stderr)
            raise ValueError("No actions: ", str(state))
        return chosen

class PoliteMinMaxClientPlayer(MinMaxClientPlayer):

    def _precompute(self):
        pass

class LocalServerPlayer(CheckersServerBase):

    def __init__(self, state=None, color=None, verbose=False, **kwargs):
        """Pass a color, I guess.  For a change of pace or whatever."""
        super().__init__()
        self._show_move = ((lambda m: print(m, file=sys.stderr)) if verbose
                           else lambda x: None)
        self.__board = state or Bitboard32State()

        self._friend_count = self._board.count_friends()
        self._foe_count = self._board.count_foes()
        self._moves_since_piece_taken = 0

        self._secret_client = PoliteMinMaxClientPlayer(state=self._board,
                                                       **kwargs)
        self._color = color or random.choice(["Black", "White"])
        self._going_first = self._color == "Black"
        time.sleep(0.01)
        self._secret_client.start()
        self._secret_client.set_going_first(self._going_first)

    def start(self):
        pass

    @property
    def _board(self):
        """The board, yup"""
        return self.__board

    @_board.setter
    def _board(self, new_board):
        self.__board = new_board
        self._check_if_terminal()

    @_board.deleter
    def _board(self):
        print("Hot shit, the board got deleted in thread {}".format(self.name),
              file=sys.stderr)
        del self.__board

    def going_first(self):
        return self._going_first

    def _check_if_terminal(self):
        """called whenever the board is updated"""
        friends = self._board.count_friends()
        foes = self._board.count_foes()
        if self._friend_count == friends and self._foe_count == foes:
            self._moves_since_piece_taken += 1
        else:
            self._friend_count = friends
            self._foe_count = foes
            self._moves_since_piece_taken = 0
        # friend = "White" if self._board.plyr else "Black"
        result = None
        if friends is 0:
            result= "Black" if self._board.player() == "White" else "White"
        elif foes is 0:
            result = self._board.player()
        elif not next(self._board.actions(), None):
            result= "Black" if self._color == "White" else "White"
        elif self._moves_since_piece_taken >= 100:
            result = "Draw"

        if result in ["White", "Black"]:
            client_win = result != self._color
        else:
            client_win = False

        if result:
            self._secret_client.tell_game_over()
            raise GameOver(result=result, client_win=client_win)

    def recv_move(self, move):
        self._show_move("client played: {}".format(str(move)))
        self._board = self._board.result(move)
        # self._check_if_terminal()
        self._secret_client.recv_move(move)

    def make_move(self):
        move = self._secret_client.make_move()
        self._show_move("server played: {}".format(str(move)))
        self._board = self._board.result(move)
        # self._check_if_terminal()
        return move
