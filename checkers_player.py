#!/usr/bin/env python3

from checkers import Checkers
import functools
import random
import time
import json
import gc

CACHE_SIZE = 10001

weights = json.load(open("weights_example.json","r"))

def paramLookup(state): #will be expanded later
    return {'friend_count' : state.board.count_friends(), 'foe_count' : state.board.count_foes(),
            'friend_kings' : state.board.count_friends_kings(), 'foe_kings' : state.board.count_foes_kings()}

def eval(state):
    score = 0
    paramValues = paramLookup(state)
    for parameter in weights:
        weight = weights[parameter]["weight"]
        score += weight * paramValues[parameter]
    #score = state.board.count_friends() - state.board.count_foes() + 3*state.board.count_friends_kings() - 3*state.board.count_foes_kings()
    if state.board.c_board.contents.plyr == state.player:
        return score
    return -score

# Simple alpha-beta minimax search
@functools.lru_cache(CACHE_SIZE)
def alphabeta_search(node):
    return alphabeta(node, depth = 7, alpha=float('-inf'), beta=float('inf'), maximum=True)

def alphabeta(node, depth = 7, alpha=float('-inf'), beta=float('inf'), maximum=True):
    if depth == 0 or node.terminal():
        return eval(node)
    if maximum:
        val = float('-inf')
        actions = node.actions()
        action = next(actions, None)
        while action:
            child = node.result(action)
            val = max(val, alphabeta(child, depth - 1, alpha, beta, False))
            alpha = max(alpha, val)
            if beta <= alpha:
                break
            action = next(actions, None)
        return val
    else:
        val = float('inf')
        actions = node.actions()
        action = next(actions, None)
        while action:
            child = node.result(action)
            val = min(val, alphabeta(child, depth - 1, alpha, beta, True))
            beta = min(beta, val)
            if beta <= alpha:
                break
            action = next(actions, None)
        return val

if __name__ == "__main__":
    random.seed(time.time())
    game = Checkers()
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
    count = 10
    while not error and count>0:
        start_time = time.time()
        game.reset(False)
        print("Start {}:".format(count))
        while not game.finished():
            actions = game.actions()
            action = next(actions, None)
            bestScore = float('-inf')
            if action:
                move_list = [action]
            while action:
                score = alphabeta_search(game.result(action))
                if float(score) > bestScore:
                    bestScore = score
                    move_list = [action]
                elif score == bestScore:
                    move_list.append(action)
                action = next(actions, None)
            index = random.randint(0, len(move_list)-1)
            error = game.play(move_list[index])
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
