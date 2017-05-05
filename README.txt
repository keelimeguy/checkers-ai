
Keelin Becker-Wheeler
Jonathan Homburg
Philip Ira
Oliver Kisielius

CSE4705 - Final: Checkers Learner

###################################################################################
Running code:
###################################################################################
  First, while in the directory '/checkers-ai/checkers/c':
    run: 'make'
  Then, while in the directory '/checkers-ai':
    run: 'python setup.py develop'
  Finally, in the same directory:
    run: 'python -m unittest'
    or run: 'python -m checkers.game_example -h'
###################################################################################


###################################################################################
--------------Note: Our code cannot run on windows!--------------
###################################################################################
Your success in running the code is dependent on the installed packages and version numbers of your environment.
We successfully ran the code in a virtual machine running Ubuntu 14.04 on a 4 GB, 2GHZ, 64-bit Windows 10 machine.

###################################################################################


Some notes on C code 32 representation:
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
                with bits in 0xXXXXXXXX ordered 32,31,..,2,1 (each X corresponding to 4-bits, i.e. a row)

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

That's all.
