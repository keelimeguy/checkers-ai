from state_superclass.py import CheckersGameState


WC = "w"
WK = "W"
BC = "b"
BK = "B"


class EightXEightGameState(CheckersGameState):
"""Uses a double array to represent the board"""

	def Variables(self)
		self.playerBlack = "true"
		"""rows and columns"""
		r,c = 8,8;
		Board = [[ 0 for x  in range(r)] for y in range(c)]

		for r in range(len(board))
		 	for c in range(len(board))
		 	 	Board[r][c] = "-" 

		 	 	

