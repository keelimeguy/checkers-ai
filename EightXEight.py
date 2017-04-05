from state_superclass.py import CheckersGameState


WC = "w"
WK = "W"
BC = "b"
BK = "B"

class EightXEightGameState(CheckersGameState):
	"""Uses a double array to represent the board"""
	def Variables(self):
		self.playerBlack = "true"
		r,c = 8,8;
		Board = [[0 for x in range(r)] for y in range(C)]
		for r in range(r):
			for c in range(c):
				Board[r][c] = "-"
		print Board




