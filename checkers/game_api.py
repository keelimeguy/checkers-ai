import sys
import abc
from threading import Thread

class GameOver(Exception):
    """Thrown by a player when the game has ended

    This shouldn't be thrown until the communication with the server is
    finished, if that's happening
    """

    def __init__(self, *args, result=None, **kwargs):
        # result should be "Black" "White" or "Draw"
        super().__init__(*args, **kwargs)
        self.result = result

# class ChoosyCheckersGame(CheckersGame):

#     def __init__(self, *args, choosy_player=None,
#                  other_player=None, **kwargs):
#         # first_player = (choosy_player if choosy_player.going_first()
#         #                 else other_player)
#         if choosy_player.going_first():
#             super().__init__(state, choosy_player, other_player, **kwargs)
#         else:
#             super().__init__(state, other_player, choosy_player, **kwargs)

class CheckersGame(Thread):

    # class GameEndedByPlayer(Exception):
    #     pass

    def __init__(self, player1, player2):
        """Player1 goes first.  The two players should already know the state
        of the board and whose move it is.
        """
        # self.state = state
        super().__init__()  # just preparing for the conversion to Thread
        self.next_player = player1  # this, we'll be switching around
        self.benchwarmer_player = player2
        self.result = None

    def step(self):
        move = self.next_player.make_move() # the blocking part of the loop
        if move is None:
            print("self.next_player made a None move :( {}".format(
                self.next_player),
                  file=sys.stderr)
        self.benchwarmer_player.recv_move(move)
        self.next_player, self.benchwarmer_player = (
            self.benchwarmer_player, self.next_player)

    # hey, uh, I think I see how CheckersGame could be massaged into a Thread
    # subclass...
    def run(self):
        """Make the game happen and return the winner"""
        while True:
            try:
                self.step()
            except GameOver as g:
                #  maybe tell both players who won and how
                self.result = g.result
                return

class CheckersPlayerBase(object):
    """This is essentially an interface. See https://pymotw.com/3/abc/

    Checkers players should be subclasses of this.
    """
    __metaclass__ = abc.ABCMeta  # don't worry about this

    @abc.abstractmethod
    def recv_move(self, move):
        """Receive a move played by the opponent"""

    @abc.abstractmethod
    def make_move(self):
        """Return a real zinger of a move"""


class CheckersServerBase(CheckersPlayerBase):
    """Checkers servers choose who goes first"""

    @abc.abstractmethod
    def going_first(self):
        """Return True if the (remote) opponent will be Black (go first)"""

class CheckersClientBase(CheckersPlayerBase):
    """Clients need to find out who's going first.  It's better to find this
    out before you need to play a move so you don't pre-compute openings for
    the wrong player."""

    @abc.abstractmethod
    def set_going_first(self, go_first):
        """Pass True if this client has the first move"""

    @abc.abstractmethod
    def tell_game_over(self):
        """Call this when you want the thread to stop executing after the game"""



class LocalServerPlayer(CheckersServerBase):
    """We learn by playing against this jerk"""
    NotImplemented

class CoarseLearningPlayer(CheckersClientBase):
    NotImplemented
