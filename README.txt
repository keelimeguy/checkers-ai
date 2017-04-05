
Keelin Becker-Wheeler
Jonathan Homburg
Philip Ira
Oliver Kisielius

CSE4705 - HW4: Checkers Representations

Running code:
In your command line, navigate to the "./c/" directory (probably using "cd" commands)
From there you may run the precompiled executable "checkers32.exe" (the command "./checkers32.exe" should work if you are in the "./c/" directory)
This code will show a state, it's available moves, and the results of taking the first available move twice.
In order to change the starting state of the board you must change it within "./c/main.c" according to these guidelines:
    - The lines:  board->b = 0x00e06021;
                  board->w = 0x00000200;
                  board->k = 0x00000200;
                  board->plyr = 1;
      will determine the starting state. You should only need to change these lines.

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

After making these changes to the starting board in "./c/main.c", the code will need to be compiled.
To compile the changed code, running the command "make" while you are still in the "./c" directory in command line should work.
(If that does not work try "gcc -ggdb3 main.c checkers32_calc.c checkers32.c -o checkers32.exe")
Now the edited code should be compiled and able to be ran by starting "checkers32.exe" (using the command "./checkers32.exe" for instance)

Compiling the code requires gcc (the c compiler) to be on your machine, which it likely already is

-------------------------------------------------------------------
-------------------------------------------------------------------

for sample output see files:
"sample_out_full_game_first_move.txt"
"sample_out_multi_jump_forced_loss.txt"
"sample_out_test_cases.txt"
"sample_out_sparse_full_game.txt"

Notice: Most implementations are written in python with some pieces written in C, which are called from python using c_lists
        Choices in these languages are made with consideration for speed

8 by 8 array: "./EightXEight.py"
    pros: direct representation
    cons: higher space, less speed

32 element array: "./c/checkers32.c"
    pros: speed in calculating moves
    cons: more complexity

35 element array: "./samuel_state.py"
    pros: ease and speed in calculating moves
    cons: less complexity

Sparse representation: "./CheckersStateSparse.py"
    pros: low space, ease in finding where a given piece is at
    cons: difficulty in finding what is at a given board position, low speed
