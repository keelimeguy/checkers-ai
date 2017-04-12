from state_superclass import CheckersGameState
"""Mac's Contribution holy snap what is python  and why am i learning it in one evening"""

# colors for the pieces

WC = "w"
WK = "W"
BC = "b"
BK = "B"

class EightXEightGameState(CheckersGameState):
    """Uses a double array to represent the board"""

    class Move:
        def __init__(self, *spaces):
            self.spaces = spaces

        def __str__(self):
            return ":".join("({}:{})".format(x[0], x[1]) for x in self.spaces)

    def __init__(self):
        self.Black = True
        self.populateDoubleArray()

    def populateDoubleArray(self):
        self.Board = [["+" for x in range(8)] for y in range(8)]

        for row in range(8):
            for col in range(8):
                if col%2 != row%2:
                    continue
                if row < 3:
                    self.Board[row][col] = 'b'
                elif row > 4:
                    self.Board[row][col] = 'w'
                else:
                    self.Board[row][col] = None
            print(''.join(y or '-' for y in self.Board[row]))

    def actions(self):
        """List all possible moves for the current player"""
        okay_to_move = "bB" if self.Black else "wW"
        kings = "BW"
        results = []
        found_jump = False
        for row_i, row in enumerate(self.Board):
            for col_i, piece in enumerate(row):
                if move and move in okay_to_move:
                    if self.has_jump(row_i, col_i):
                        if not found_jump:  # this is the first jump
                            results.clear()  # so these non-jumps are illegal
                            found_jump = True
                        results.extend(find_jumps(row_i, col_i))
                    elif not found_jump:
                        results.extend(find_simple_moves(row_i, col_i))
        return results

    def occupied(self, r, c):
        return self.Board[r][c] and self.Board[r][c] in "bwBW"


    def find_simple_moves(self, row_i, col_i):
        """Find non-jump moves for this piece"""
        b_candidates = [(row_i - 1, col_i - 1),
                        (row_i - 1, col_i + 1)]
        w_candidates = [(row_i + 1, col_i - 1),
                        (row_i + 1, col_i + 1)]
        if self.Board[row_i][col_i] == 'w':
            cands = w_candidates
        elif self.Board[row_i][col_i] == 'b':
            cands = b_candidates
        elif self.Board[row_i][col_i] in "WB":
            cands = w_candidates + b_candidates
        else:
            raise ValueError("What even is this piece?",
                              self.Board[row_i][col_i])
        return [p for p in cands if not self.occupied(*p)]

    def find_jumps(self, r, c):
        if self.Board[r][c] in "BW":
            return self.find_king_jumps(r, c)
        else:
            return self.find_peon_jumps(r, c)

    def find_peon_jumps(self, r, c):
        """This one is easier. You never jump backwards, even if the piece is promoted"""
        # don't check self.Board[r][c] in case this is a recursive case
        vert_mv = -1 if self.Black else 1
        enemy = "wW" if self.Black else 'bB'
        results = []  # list of lists of (coord,inates)
        for horiz_mv in [-1, 1]:
            if (self.Board[r+vert_mv][c+horiz_mv] in enemy
                and not self.occupied(r+2*vert_mv, c+2*horiz_mv)):  # TODO fix index-out-of-bounds bug
                for tail in self.find_peon_jumps(r+2*vert_mv, c+2*horiz_mv):
                    results.append([(r+2*vert_mv, c+2*horiz_mv), tail])
        return results  # notice the base case is [], except that actually it will go off the board and throw an error whenever it possibly can. Not hard to fix except at 4:35 AM.






    #def move(self, ourMove)


    def player(self):
        if self.Black:
            return "Black"
        else:
            return "White"

    #def movesBlack(boardStatus):

    def __str__(self):
        return "{}\n\n{}'s move".format(
                '\n'.join(''.join(y or '-' for y in row) for row in self.Board),
                self.player()
            )