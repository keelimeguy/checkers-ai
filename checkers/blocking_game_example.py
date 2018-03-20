import argparse
import gc
import sys
import json
import os.path
import random
import time

import checkers.heuristics as heuristics

try:
    from math import inf
except ImportError:
    inf = float('inf')

from checkers.game_api import GameOver
from checkers.players import SimpleMcCartneyServerPlayer

weights_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),"weights.json")

if __name__ == "__main__":
    random.seed(time.time())
    parser = argparse.ArgumentParser(description='Plays a given number of games with a given opponent using the given user number.')
    parser.add_argument('-o', '--opponent', type=int, default=0, help='The opponent user number.')
    parser.add_argument('-u', '--user', type=int, default=5, help='Your user number (5 or 6).')
    parser.add_argument('-c', '--count', type=int, default=1, help='Number of consecutive games to play.')
    parser.add_argument('-w', '--weights', default=weights_file, help='File with weight constants')
    parser.add_argument('-v', '--verbose', default=False, help='\'True\' if you want to display each message sent between the client and server')
    args = parser.parse_args()
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

    error = False
    while not error and count>0:
        start_time = time.time()
        print("Start {}:".format(count))
        game = SimpleMcCartneyServerPlayer(args.opponent, args.user==6, 1 if args.verbose else 0)
        try:
            # game.start()
            while True:
                actions = game.board.list_actions()
                bestScore = -inf
                move_list = []
                if len(actions) != 0:
                    if len(actions) == 1:
                        result = game.recv_move(actions[0])
                        if isinstance(result, GameOver):
                            raise result
                    else:
                        for act in actions:
                            score = heuristics.alphabeta_search(game.board.result(act), game._client_is_white, weights)
                            if float(score) > bestScore:
                                bestScore = score
                                move_list = [act]
                            elif score == bestScore:
                                move_list.append(act)
                        index = random.randint(0, len(move_list)-1)
                        result = game.recv_move(move_list[index])
                        if isinstance(result, GameOver):
                            raise result
                else:
                    error = True
                    print("Error: No actions available.")
                    break
        except GameOver as inst:
            print("GameOver Exception: ", inst.result, file=sys.stderr)
            if inst.result:
                game.show_game()
                if inst.result == "Draw":
                    draws+=1
                elif inst.result == ("White" if game._client_is_white else "Black"):
                    wins+=1
                elif inst.result == ("Black" if game._client_is_white else "White"):
                    losses+=1
                else:
                    print("Unknown result? : " + inst.result)
            else:
                error = True
        time_diff = time.time() - start_time
        if time_diff > max_time:
            max_time = time_diff
        if time_diff < min_time or num == 0:
            min_time = time_diff
        total_time+=time_diff
        print("Finished in {}s\n".format(time_diff))
        num+=1
        count-=1

        game = None
        gc.collect()

    # print("eval cache: ", eval.cache_info())
    print("Stats: {}w:{}d:{}l\navg time = {}s\nmax time = {}s\nmin time = {}s".format(wins, draws, losses, total_time/num, max_time, min_time))
