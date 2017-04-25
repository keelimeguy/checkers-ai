#!/usr/bin/env python3

import sys
from checkers.checkers import Checkers

import argparse
import functools
import random
import time
import json
import sys
import os.path
import gc

CACHE_SIZE = 10001

weights_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),"weights_example.json")

def paramLookup(board):
    return {'friend_count' : board.count_friends(),
            'foe_count' : board.count_foes(),
            'friend_kings' : board.count_friends_kings(),
            'foe_kings' : board.count_foes_kings(),
            'friend_pawns' : board.count_friends_pawns(),
            'foe_pawns' : board.count_foes_pawns(),
            'safe_friend_pawns': board.count_safe_friends_pawns(),
            'safe_foe_pawns' : board.count_safe_foes_pawns(),
            'safe_friend_kings' : board.count_safe_friends_kings(),
            'safe_foe_kings' : board.count_safe_foes_kings(),
            'movable_friend_pawns' : board.count_movable_friends_pawns(),
            'movable_foe_pawns' : board.count_movable_foes_pawns(),
            'movable_friend_kings' : board.count_movable_friends_kings(),
            'movable_foe_kings' : board.count_safe_foes_kings(),
            'friend_distance_promotion' : board.aggregate_distance_promotion_foes(),
            'foe_distance_promotion' : board.aggregate_distance_promotion_foes(),
            'unoccupied_promotion_friends' : board.count_unoccupied_promotion_friends(),
            'unoccupied_promotion_foes' : board.count_unoccupied_promotion_foes(),
            'defender_friends' : board.count_defender_pieces_friends(),
            'defender_foes' : board.count_defender_pieces_foes(),
            'attack_pawn_friends' : board.count_attack_pawns_friends(),
            'attack_pawn_foes' : board.count_attack_pawns_foes(),
            'center_pawn_friends' : board.count_center_pawns_friends(),
            'center_pawn_foes' : board.count_center_pawns_foes(),
            'center_king_friends' : board.count_center_kings_friends(),
            'center_king_foes' : board.count_center_kings_foes(),
            'diagonalmain_pawn_friends' : board.count_diagonalmain_pawns_friends(),
            'diagonalmain_pawn_foes' : board.count_diagonalmain_pawns_foes(),
            'diagonalmain_king_friends' : board.count_diagonalmain_kings_friends(),
            'diagonalmain_king_foes' : board.count_diagonalmain_kings_foes(),
            'diagonaldouble_pawn_friends' : board.count_diagonaldouble_pawns_friends(),
            'diagonaldouble_pawn_foes' : board.count_diagonaldouble_pawns_foes(),
            'diagonaldouble_king_friends' : board.count_diagonaldouble_kings_friends(),
            'diagonaldouble_king_foes' : board.count_diagonaldouble_kings_foes(),
            'loner_pawn_friends' : board.count_loner_pawns_friends(),
            'loner_pawn_foes' : board.count_loner_pawns_foes(),
            'loner_king_friends' : board.count_loner_kings_friends(),
            'loner_king_foes' : board.count_loner_kings_foes(),
            'holes_friends' : board.count_holes_friends(),
            'holes_foes' : board.count_holes_foes(),
            'triangle_friends' : board.triangle_friends(),
            'triangle_foes' : board.triangle_foes(),
            'oreo_friends' : board.oreo_friends(),
            'oreo_foes': board.oreo_foes(),
            'bridge_friends' : board.bridge_friends(),
            'bridge_foes' : board.bridge_foes(),
            'dog_friends' : board.dog_friends(),
            'dog_foes' : board.dog_foes(),
            'corner_pawn_friends' : board.pawn_corner_friends(),
            'corner_pawn_foes' : board.pawn_corner_foes(),
            'corner_king_friends' : board.king_corner_friends(),
            'corner_king_foes' : board.king_corner_foes()}

def eval(state):
    score = 0
    param_values = paramLookup(state.board)
    for parameter in weights:
        weight = weights[parameter]["weight"]
        score += weight * param_values[parameter]
    if state.board.c_board.contents.plyr == state.player:
        return score
    return -score

# Simple alpha-beta minimax search
@functools.lru_cache(CACHE_SIZE)
def alphabeta_search(node):
    return alphabeta(node, depth=7, alpha=float('-inf'), beta=float('inf'), maximum=True)

def alphabeta(node, depth=7, alpha=float('-inf'), beta=float('inf'), maximum=True):
    # TODO make unit tests for this
    if depth == 0 or node.terminal():
        return eval(node)
    if maximum:
        val = float('-inf')
        choose = max
    else:
        val = float('inf')
        choose = min
    for action in node.actions():
        child = node.result(action)
        val = choose(val, alphabeta(child, depth=(depth-1), alpha=alpha,
                                    beta=beta, maximum=(not maximum)))
        if maximum:
            alpha = choose(alpha, val)
        else:
            beta = choose(beta, val)
        if beta <= alpha:
            break
    return val

if __name__ == "__main__":
    random.seed(time.time())
    parser = argparse.ArgumentParser(description='Plays a given number of games with a given opponent using the given user number.')
    parser.add_argument('-o', '--opponent', type=int, default=0, help='The opponent user number.')
    parser.add_argument('-u', '--user', type=int, default=5, help='Your user number (5 or 6).')
    parser.add_argument('-c', '--count', type=int, default=1, help='Number of consecutive games to play.')
    parser.add_argument('-w', '--weights', default=weights_file, help='File with weight constants')
    parser.add_argument('-v', '--verbose', default=False, help='\'True\' if you want to display each message sent between the client and server')
    args = parser.parse_args()
    game = Checkers(args.opponent, args.user==6)
    final = ""
    error = False
    wins = 0
    losses = 0
    draws = 0
    num = 0
    total_time = 0
    max_time = 0
    min_time = 0

    # How many times to run a game
    count = args.count

    global weights
    weights = json.load(open(args.weights, 'r'))

    while not error and count>0:
        start_time = time.time()
        game.reset(args.verbose=='True')
        print("Start {}:".format(count))
        while not game.finished():
            error = True
            actions = game.actions()
            move_list = [next(actions, None)]
            bestScore = float('-inf')
            if move_list[0]:
                for act in actions:
                    score = alphabeta_search(game.result(act))
                    if float(score) > bestScore:
                        bestScore = score
                        move_list = [act]
                    elif score == bestScore:
                        move_list.append(act)
                index = random.randint(0, len(move_list)-1)
                error = game.play(move_list[index])
                if error:
                    break
            else:
                error = True
                break
        if not error:
            final = game.show_game()
            if final == "DRAW!":
                draws+=1
            elif final == "WON!":
                wins+=1
            elif final == "LOSE!":
                losses+=1
            else:
                print("Unknown final? : " + final)
        time_diff = time.time() - start_time
        if time_diff > max_time:
            max_time = time_diff
        if time_diff < min_time or num == 0:
            min_time = time_diff
        total_time+=time_diff
        print("Finished in {}s\n".format(time_diff))
        num+=1
        count-=1
        gc.collect()

    print("Stats: {}w:{}d:{}l\navg time = {}s\nmax time = {}s\nmin time = {}s".format(wins, draws, losses, total_time/num, max_time, min_time))
