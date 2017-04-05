class CheckersGameState:
    """A superclass for instance testing.

    Nothing else seems very useful to share, so it'll just be empty.

    (There's no obligation to fill this with abstract methods.)

    By the way, if you begin class and function definitions with a string like
    this, you can access it by running the built-in help() on the objects you
    create.
    """
    pass

def parse_board_string(board_rep):
    """Take a board representation in the canonical format (see unit tests) and
    return tuple (L, P) where

    L is a list of tuples (row, column, character) with the locations and types
    (character "W", "w", "B", or "b") of all the checkers

    P is the current player, "White" or "Black"
    """
    lines = board_rep.strip().split()  # split on whitespace (e.g. newlines)
    pieces = []
    for row, line in enumerate(lines[:8][::-1]):
        for column, char in enumerate(line.strip()):
            if char in 'wWbB':
                if (column % 2) == (row % 2):
                    pieces.append((row, column, char))
                else:
                    raise ValueError(
                        "Bad location ({}, {}) for piece '{}'".format(
                            row, column, char))
            elif char not in "-+":
                raise ValueError("Unexpected char {} found in board "
                                 "description at ({}, {})".format(char,
                                                                  row,
                                                                  column))

    player = lines[8][:5]
    if player not in ["White", "Black"]:
        raise ValueError("Unknown value '{}' for player "
                         "- expected 'Black' or 'White'".format(player))
    return (pieces, player)
