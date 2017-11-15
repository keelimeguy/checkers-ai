import abc

from checkers.state import Bitboard32State
from checkers.alphabeta import AlphaBeta

class CheckersPlayer:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def play_move(self, board):
        raise NotImplementedError("I don't even know how to move")

def is_game_over(board):
    return not bool(list(board.actions()))

def both_have_pieces(board):
    return board.count_friends() > 0 and board.count_foes() > 0

class SimpleCheckersGame:

    def __init__(self, player1, player2):
        self.board = Bitboard32State.from_string("""+b+b+b+b
b+b+b+b+
+b+b+b+b
-+-+-+-+
+-+-+-+-
w+w+w+w+
+w+w+w+w
w+w+w+w+

Black's move""")
        self.players = [player1, player2]

    def play(self, training=False):
        """Play and return the winner (or None if draw)"""
        if training:
            stale_moves = 18
        else:
            stale_moves = 200  # number of useless moves for a draw (tournament rules)
        turns_since_event = 0
        number_of_pieces = count_pieces(self.board)
        number_of_kings = count_kings(self.board)
        turn = 0
        while not is_game_over(self.board) and turns_since_event < stale_moves:
            move = self.players[turn].play_move(self.board)
            self.board = self.board.result(move)
            turn = (turn + 1) % 2
            if (count_pieces(self.board) == number_of_pieces and
                count_kings(self.board) == number_of_kings):
                turns_since_event += 1
            else:
                number_of_pieces = count_pieces(self.board)
                number_of_kings = count_kings(self.board)
                turns_since_event = 0
        if both_have_pieces(self.board):
            # It's a draw
            return None
        else:
            # players[turn] has no pieces, so the other wins
            return self.players[(turn + 1) % 2]

def count_pieces(board):
    return board.count_friends() + board.count_foes()

def count_kings(board):
    return board.count_friends_kings() + board.count_foes_kings()

class HeuristicCheckersPlayer(CheckersPlayer):

    def __init__(self, heuristic, depth=5):
        self.heuristic = heuristic
        # self.depth = depth
        self.alphabeta = AlphaBeta(self.heuristic, default_depth=depth)

    def play_move(self, board):
        options = list(board.actions())
        if len(options) == 1:
            return options[0]
        elif len(options) < 1:
            raise Exception("game is over but player was asked to move")
        return max(options,
                   key=lambda opt: self.alphabeta.ab_dfs(board.result(opt), maximum=False))
