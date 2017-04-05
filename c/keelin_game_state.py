from ..state_superclass import CheckersGameState

class KeelinGameState(CheckersGameState):
    """Uses 32-slot representation of checkerboards."""

    def __init__(self, guts=None):
        self.board = guts

    def

