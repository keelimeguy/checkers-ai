import random
from checkers.simple_game_api import SimpleCheckersGame, HeuristicCheckersPlayer
from checkers.state import Bitboard32State as BoardState
from checkers.heuristics import BoardEvaluator
import json
import argparse
import sys
import math

mutation_rate = 0.1
population_size = 25

def breed_weight_dicts(dict1, dict2):
    assert dict1.keys() == dict2.keys()
    mixdict = {}
    for key in dict1:
        ratio = random.random()
        
        mixdict[key] = ratio * dict1[key] + (1 - ratio) * dict2[key]

    return mixdict

def mutate(weight_dict):

    for key in weight_dict:
        if random.random() < mutation_rate:
            weight_dict[key] = weight_dict[key] * random.choice([-1, 0.5, 2])

def heuristic_names_list():
    return [name for name in dir(BoardState) if (
        'friend' in name or
        'foe' in name or
        'count' in name) and name not in ("count_holes", "count_loner", "count_movable_kings_check", "count_movable_pawns_check", "count_player_and_mask")]

def make_population(size=population_size):
    # popl = []
    # for i in range(size):
    #     popl.append(make_random_member())
    # return popl
    return [make_random_member() for _ in range(size)]

def make_random_member():
    new_weights = {}
    for key in heuristic_names_list():
        new_weights[key] = random.choice(range(-25, 26))
    return new_weights
    

def dump_population(popl, filename):
    with open(filename, 'w') as f:
        json.dump(popl, f)

def load_population(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def make_scores(population, depth=1):
    scores = [0] * len(population)
    for i, i_weights in enumerate(population):
        for j, j_weights in enumerate(population):
            if i == j:
                continue
            print("fighting {} and {} -- winner: ".format(i, j), file=sys.stderr, end="")
            winner = fight(i_weights, j_weights, depth=depth)
            if winner == i_weights:
                scores[i] += 1
                print(i, file=sys.stderr)
            elif winner == j_weights:
                scores[j] += 1
                print(j, file=sys.stderr)
            elif winner is None:
                scores[i] += 0.2
                scores[j] += 0.2
                print("tie", file=sys.stderr)
    return scores

def fight(weight_set_0, weight_set_1, depth=1):
    def mk_player(weights):
        return HeuristicCheckersPlayer(BoardEvaluator(weights), depth=depth)
    player0 = mk_player(weight_set_0)
    player1 = mk_player(weight_set_1)
    assert player0 != player1
    winner = SimpleCheckersGame(player0, player1).play(training=True)
    if winner is None:
        return None
    elif winner is player0:
        return weight_set_0
    elif winner is player1:
        return weight_set_1
    else:
        raise Exception("The winner is not a player")

def select_based_on_scores(population, scores):
    exponent = math.log(len(population))  # this feels like a good idea
    scores = [score ** exponent for score in scores]
    sumscore = sum(scores)
    needle = random.random() * sumscore  # like spinning a needle
    so_far = 0
    for i, (member, score) in enumerate(zip(population, scores)):
        so_far += score
        if so_far >= needle:
            if score < (2 + len(scores) * 0.2)**exponent:
                print("Breeding a homunculus instead of", i, file=sys.stderr)
                return make_random_member()
            else:
                print("Breeding {}, score: {}".format(i, score), file=sys.stderr)
            return member
    raise Exception("Something went horribly wrong in selection: scores sum to {}"
                    ", needle is {}".format(sumscore, needle))


def main(generations, pop_size=None, load_from=None, save_to=None, depth=1):

    if load_from:
        population = load_population(load_from)
        if not pop_size:
            pop_size = len(population)
    else:
        if not pop_size:
            pop_size = population_size
        population = make_population(size=pop_size)

    for g in range(generations):
        scores = make_scores(population, depth=depth)
        next_gen = [population[max(range(len(population)), key=lambda i: scores[i])],
                    make_random_member()]  # hard-coding these two ensures that something interesting is always happening
        for _ in range(2, pop_size):
            parent0 = select_based_on_scores(population, scores)
            parent1 = select_based_on_scores(population, scores)
            child = breed_weight_dicts(parent0, parent1)
            mutate(child)
            next_gen.append(child)
        print("Finished generation {}".format(g), file=sys.stderr)
        population = next_gen
        if save_to:
            dump_population(population, save_to)

    if save_to:
        dump_population(population, save_to)
    else:
        print(json.dumps(population))

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Do genetic algo to make checkers players")
    parser.add_argument("-p", "--pop-size", type=int, default=0, help="size of population")
    parser.add_argument("-g", "--generations", type=int, default=10, help="number of generations")
    parser.add_argument("-i", "--infile", default=None, type=str, help="file to load population (omit for random population)")
    parser.add_argument("-o", "--outfile", default=None, type=str, help="file to save results to")
    parser.add_argument("-d", "--search-depth", default=1, type=int, help="depth of minimax search for checkers players")
    args = parser.parse_args()
    print(args)
    main(args.generations, pop_size=args.pop_size, load_from=args.infile, save_to=args.outfile, depth=args.search_depth)
