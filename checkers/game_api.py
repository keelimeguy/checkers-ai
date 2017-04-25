

class GameOver(Exception):
    """Thrown by a player when the game has ended

    This shouldn't be thrown until the communication with the server is
    finished, if that's happening
    """

    def __init__(self, *args, result=None, **kwargs):
        # result should be "Black" "White" or "Draw"
        super.__init__(*args, **kwargs)
        self.winner = winner

# class ChoosyCheckersGame(CheckersGame):

#     def __init__(self, *args, choosy_player=None,
#                  other_player=None, **kwargs):
#         # first_player = (choosy_player if choosy_player.going_first()
#         #                 else other_player)
#         if choosy_player.going_first():
#             super().__init__(state, choosy_player, other_player, **kwargs)
#         else:
#             super().__init__(state, other_player, choosy_player, **kwargs)

class CheckersGame:

    # class GameEndedByPlayer(Exception):
    #     pass

    def __init__(self, player1, player2):
        """Player1 goes first.  The two players should already know the state
        of the board and whose move it is.
        """
        # self.state = state
        # super().__init__()  # just preparing for the conversion to Thread
        self.next_player = player1  # this, we'll be switching around
        self.benchwarmer_player = player2

    def step(self):
        move = self.next_player.make_move() # the blocking part of the loop
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
                return g.result


# class CheckersPlayerBase:
#     pass

# Maybe make clear(er) the fact that some players are servers and some are client, 
class McCartneyServerPlayer:
    NotImplemented

class HumanTypingFranticallyClientPlayer:
    NotImplemented

class HumanTypingFranticallyServerPlayer:
    """You thought it couldn't get worse, did you?"""
    NotImplemented

class MinMaxClientPlayer:
    NotImplemented

class LocalServerPlayer:
    """We learn by playing against this jerk"""
    NotImplemented

class CoarseLearningPlayer:
    NotImplemented
