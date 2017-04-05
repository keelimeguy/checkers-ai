
Keelin Becker-Wheeler
Jonathan Homburg
Philip Ira
Oliver Kisielius

CSE4705 - HW4: Checkers Representations

for sample output see files:
"sample_out_full_game_first_move.txt"
"sample_out_multi_jump_forced_loss.txt"
"sample_out_test_cases.txt"
"sample_out_sparse_full_game.txt" (sparse representation only)

Notice: Most implementations are written in python with some pieces written in C, which are called from python using c_lists
Choices in language are made with consideration for speed

8 by 8 array: EightXEight.py
    pros: direct representation
    cons: higher space, less speed

32 element array: c/checkers32.c
    pros: speed in calculating moves
    cons: more complexity

35 element array: samuel_state.py
    pros: ease and speed in calculating moves
    cons: less complexity

Sparse representation: CheckersStateSparse.py
    pros: low space, ease in finding where a given piece is at
    cons: difficulty in finding what is at a given board position, low speed
