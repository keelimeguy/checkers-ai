
Keelin Becker-Wheeler
Jonathan Homburg
Philip Ira
Oliver Kisielius

CSE4705 - Final: Checkers Learner


###################################################################################
Running code:
  While in the directory '/checkers-ai', run 'python -m checkers.checkers_player -h'
###################################################################################
Also: Follow Olivers instructions at the bottom to install virtualenv (probably optional at this point, might be necessary later)


Organization:

- checkers_player.py has the code which runs the player with certain evaluation  and state searching functions
      - this is the file which should be considered the most while writing other code which plays checkers, with added learning algorithms perhaps
      - can also provide statistics and visual representation of completed games
- checkers.py has the code to represent and control a checkers game played with the server
      - requires bitboard_32_state.py, the checkers board state, which is a python wrapper for checkers32.c
            - checkers32.c is the higher level representation of the base bitboards in c
            - checkers32_calc.c is provides helpful computational functions so that checkers32.c may work
      - requires sam_server.py, the server protocol interface, which is a python wrapper for mysockets.c
            - mysockets.c provides the interfacing and protocol for communicating with the server (through sockets library)

Checkers -> | -> CheckersState -> BitboardState -> checkers32.c
            | -> SamServer -> mysockets.c



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


###############################################################################
###   Installation:
###############################################################################
You want Python version at least 3.5 (the first version with a fast C
implementation of OrderedDict).

Use a virtual environment!  This is normal Python procedure.  If you don't use
virtualenvs, you'll eventually install conflicting packages (like PIL and
pillow) and stuff will break.

All a virtualenv does is 

########## Installing virtualenv (and using it) ###############################

To install virtualenvwrapper, follow the instructions for your distro here:

        https://virtualenvwrapper.readthedocs.io/en/latest/

The link above has too much information. Basically what you want to do is:

        my-package-manager install python-virtualenvwrapper

        # edit ~/.bashrc to source some scripts
        # I added these lines to my ~/.zshrc, for example:
        export WORKON_HOME=~/.config/.virtualenvs
        source /usr/bin/virtualenvwrapper.sh
        export PIP_REQUIRE_VIRTUALENV=true


        # You want at least python3.5.
        # After this example, `which python` returns
        #   /home/oliver/.config/.virtualenvs/ai/bin/python
        # and `python --version` returns
        #   Python 3.6.0
        # (It'll probably change add "(ai-env)" to your shell prompt, too.)
        mkvirtualenv --python=$(which python3.6) ai-env

        # To exit the virtualenv again:
        deactivate
        # Now `which python` returns "/usr/bin/python" as normal

        # to reactivate a virtualenv you've created:
        workon ai-env


To see a list of virtualenvwrapper commands, simply type

        virtualenvwrapper

The only commands I ever use are mkvirtualenv, workon, deactivate, and
rmvirtualenv, but I'm sure the others are lovely, too.


########## Installing the package #############################################

From the current directory (checkers-ai), with your virtualenv active, run

        python setup.py develop

Installing this way allows you to make changes and see the effects immediately
without reinstalling.  ($WORKON_HOME/ai-env/lib/python3.6/site-packages will
now have a bunch of symbolic links to the code in the repo.)

Notice that now you can run python in any directory and import the checkers code with

        import checkers.c.structs

or what-have-you.


########## Running the unit tests #############################################

        python -m unittest

That's all.
