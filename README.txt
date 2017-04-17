
Keelin Becker-Wheeler
Jonathan Homburg
Philip Ira
Oliver Kisielius

CSE4705 - Final: Checkers Learner

Evaluation Function Parameters:
• Difference between numbers of checkers of player and opponent
• Supervising selected fields on the board (opposite rows are very significant)
• Supervising the center of the board (a number of own vs opponent checkers in central 4×4 place)
• Number of kings in the central place of the board
• Number of checkers that are nearly of king state
• Number movable pieces (own vs opponent)
• Exposure of checkers (a number of checkers that potentially can be captured)
• Proximity of pieces (keep our pieces close, their pieces separated)

End Game Condition:
?
• Threshold on number of pieces left
• Threshold on number of kings
• King row cleared



--------------Note: Our code cannot run on windows!--------------


C code 32 representation:
    - b correspondes to a black bit board , w to a white, k for the king-ed pieces, and plyr is the current player ( 0 = black, 1 = white)

    - A bit board is represented as a 32 bit number with each bit cooresponding to a playable position of the board, (bit 1 (the LSB) being position 1). Using hexidecimal makes it easier to parse

    - The positions are mapped as so:
                  -  1  -  2  -  3  -  4
                  5  -  6  -  7  -  8  -
                  -  9  - 10  - 11  - 12
                  13 - 14  - 15  - 16  -
                  - 17  - 18  - 19 -  20
                  21 - 22  - 23  - 24  -
                  - 25  - 26  - 27  - 28
                  29 - 30  - 31  - 32  -
                with bits in 0xCCCCCCCC ordered 32,31,..,2,1 (each C cooresponding to 4-bits, i.e. a row)

                    An example: b = 0x00000fff
                                w = 0xfff00000
                                k = 0x00f00f00
                        will give this board:
                            +b+b+b+b
                            b+b+b+b+
                            +B+B+B+B
                            -+-+-+-+
                            +-+-+-+-
                            W+W+W+W+
                            +w+w+w+w
                            w+w+w+w+
                        with, b=black, B = black king, w = white, W = white king, - = empty playable square, + = empty non-playable square
