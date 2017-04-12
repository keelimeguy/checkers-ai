#Sparse board implementation using the "Samuel" board representation scheme

from state_superclass import CheckersGameState

class SparseGameState(CheckersGameState):
    def __init__(self, player, stateDict):
        self.player = player
        self.stateDict = stateDict

    def player(self):
        return player

    def findJumps(self, pos, piece, prevPos = 0):
        jumps = [""] #if a piece can jump it must, does it need to chain jump if able?
        if pos < 1 or pos > 35 or piece == "phantom":
            return jumps
        player = piece.owner
        stateDict = self.stateDict
        if player == "Black" or piece.isKing:
            if pos+4 in stateDict and stateDict[pos+4] != "phantom" and stateDict[pos+4].owner != player and pos+8 not in stateDict and pos+8<36 and pos+8 != prevPos:
                move = "(%d:%d)" %(pos, pos+8)
                otherjumps = self.findJumps(pos+8, piece, pos)
                jumps += [move+":"+jump for jump in otherjumps]
            if pos+5 in stateDict and stateDict[pos+5] != "phantom" and stateDict[pos+5].owner != player and pos+10 not in stateDict and pos+10<36 and pos+10 != prevPos:
                move = "(%d:%d)" %(pos,pos+10)
                otherjumps = self.findJumps(pos+10, piece, pos)
                jumps += [move+":"+jump for jump in otherjumps]
        if player == "White" or piece.isKing:
            if pos-4 in stateDict and stateDict[pos-4] != "phantom" and stateDict[pos-4].owner != player and pos-8 not in stateDict and pos-8>0 and pos-8 != prevPos:
                move = "(%d:%d)" %(pos,pos-8)
                otherjumps = self.findJumps(pos-8, piece, pos)
                jumps += [move+":"+jump for jump in otherjumps]
            if pos-5 in stateDict and stateDict[pos-5] != "phantom" and stateDict[pos-5].owner != player and pos-10 not in stateDict and pos-10>0 and pos-10 != prevPos:
                move = "(%d:%d)" %(pos,pos-10)
                otherjumps = self.findJumps(pos-10, piece, pos)
                jumps += [move+":"+jump for jump in otherjumps]
        return jumps

    def actions(self): #returns possible actions for a player to take, returns 2-tuple (prev space, next space)
        actions = []
        stateDict = self.stateDict
        jumpsAvailable = False
        for pos in stateDict:
            piece = stateDict[pos]
            if piece == "phantom":
                continue
            if piece.owner != self.player:
                continue
            jumps = self.findJumps(pos, piece)
            if len(jumps) != 1: #is jump list non-empty (excluding empty string)
                if not jumpsAvailable:
                    actions = [] #non-jumps removed from actions
                jumpsAvailable = True
                actions += [jump.strip(":") for jump in jumps if jump] #removes empty strings but preserves movements, ensures correct format
            if jumpsAvailable: #non-jumps not considered if a jump is available
                continue
            if piece.owner == "Black" or piece.isKing:
                if pos+4 not in stateDict and pos+4<36:
                    actions.append("(%d:%d)" %(pos,pos+4))
                if pos+5 not in stateDict and pos+5<36:
                    actions.append("(%d:%d)" %(pos,pos+5))
            if piece.owner == "White" or piece.isKing:
                if pos-4 not in stateDict and pos-4>0:
                    actions.append("(%d:%d)" %(pos, pos-4))
                if pos-5 not in stateDict and pos-5>0:
                    actions.append("(%d:%d)" %(pos, pos-5))
        return actions


    def result(self, movement):
        moves = movement.split(")")
        actions = [move.strip("(:").split(":") for move in moves if move] #actions of format [[pos1,pos2],[pos2,pos3],..]
        newStateDict = self.stateDict.copy()
        beginPos = int(actions[0][0])
        endPos = int(actions[-1][-1])
        del newStateDict[beginPos] #piece removed from current position
        for action in actions:
            pos1 = int(action[0])
            pos2 = int(action[1]) #piece moves from pos1 to pos2
            if pos2 in [pos1+4,pos1+5,pos1-4,pos1-5]:
                break
            elif pos2 == pos1+8:
                jumpedPos = pos1+4
            elif pos2 == pos1+10:
                jumpedPos = pos1+5
            elif pos2 == pos1-8:
                jumpedPos = pos1-4
            elif pos2 == pos1-10:
                jumpedPos = pos1-5
            else: #doesnt check if move is to phantom/offboard - not an issue as long as all movements are given from actions()
                raise Exception("illegal move: %s" %movement)
            del newStateDict[jumpedPos] #jumped piece is capture, removed from game
        newStateDict[endPos] = self.stateDict[beginPos] #piece added to the position it is moving to
        if self.player == "Black":
            if endPos in [32,33,34,35]:
                newStateDict[endPos].isKing = True
            newPlayer = "White"
        else:
            if endPos in [1,2,3,4]:
                newStateDict[endPos].isKing = True
            newPlayer = "Black"
        return SparseGameState(newPlayer, newStateDict)


    def __str__(self):
        count = 1
        out =""
        for row in range(0,8):
            rowStr = ""
            if row%2 == 0: #even indexed rows dont end in phantom square
                while count not in [5,14,23,32]:
                    rowStr += "+"
                    if count in self.stateDict:
                        rowStr += self.stateDict[count].__str__()
                    else:
                        rowStr += "-"
                    count += 1
            else: #includes phantom square
                while count not in [9,18,27,36]:
                    if count in self.stateDict:
                        rowStr += self.stateDict[count].__str__()
                    else:
                        rowStr += "-"
                    rowStr += "+"
                    count += 1
                count += 1 #ignores phantom square
            rowStr += "\n"
            out += rowStr
        out += "\n"
        out += "%s's move" %self.player
        return out

class Piece(object):
    def __init__(self, owner, position, isKing = False):
        self.owner = owner #Black or White
        self.pos = position
        self.isKing = isKing
    def __str__(self):
        if self.owner == "Black":
            if self.isKing:
                return "B"
            else:
                return "b"
        else:
            if self.isKing:
                return "W"
            else:
                return "w"

def parseStringState(player, stringState):
    stateDict = {}
    rows = startState.split('\n')
    posCount = 0;
    for row in rows:
        if row == "":
            continue
        squares = row.split("+");
        if squares[0] == "":
            squares.pop(0) #removes leading empty strings, trailing emptys will be used to place phantom positions
        for square in squares:
            posCount += 1
            if square == "-":
                continue
            elif square == "":
                stateDict[posCount] = "phantom";
                continue
            else:
                if square == "b":
                    owner = "Black"
                    isKing = False
                elif square == "B":
                    owner = "Black"
                    isKing = True
                elif square == "w":
                    owner = "White"
                    isKing = False
                elif square == "W":
                    owner = "White"
                    isKing = True
                else:
                    raise Exception("Unrecognizeed piece: " + square);
                piece = Piece(owner, posCount, isKing)
                stateDict[posCount] = piece
    return SparseGameState(player, stateDict)


startState = """
+b+b+b+b
b+b+b+b+
+b+b+b+b
-+-+-+-+
+-+-+-+-
w+w+w+w+
+w+w+w+w
w+w+w+w+
""" #+ is white space, - is empty black space
startPlayer = "Black"
currentState = parseStringState(startPlayer, startState)
print currentState

import random
while True: #run to test full game
    print ""
    actions = currentState.actions()
    if len(actions) == 0:
        print "%s Loses" %currentState.player
        break
    print "actions: %s" %str(actions)
    action = random.choice(actions)
    print "%s: %s" %(currentState.player,action)
    currentState = currentState.result(action)
    print currentState

