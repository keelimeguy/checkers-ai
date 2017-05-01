#!/usr/bin/env python3

import sys
import functools
import os
import queue

from collections import namedtuple
from threading import Thread

try:
    from math import inf
except ImportError:
    inf = float('inf')

from checkers.game_api import GameOver, CheckersClientBase

CACHE_SIZE = 65536

# @functools.lru_cache(CACHE_SIZE)
def eval(board, player, weights):
    score = 0
    param_values = param_lookup(board)
    for parameter in weights:
        if parameter == "Probability of Win": #This field used to track fitness of weight set
            continue
        weight = int(weights[parameter]["weight"])
        score += weight * param_values[parameter]()

    if board.c_board.contents.plyr == player:
        return score
    return -score

class BoardEvaluator:
    """Use this to heuristically evaluate boards for a given set of heuristic
    weights.

    The value returned needs to be multiplied by -1 if the current player is
    Min.

    Usage:

    be = BoardEvaluator(myweights, cache_size=100)
    my_board_value = be(my_board)  #  invokes the __call__ method
    my_other_board_value = be(my_other_board)
    """
    def __init__(self, weights, cache_size=100, sanity_check=True):
        """weights: should map names of functions to weights on those functions.
        (Functions with weight 0 are optimized away.)

        cache_size is for an lru_cache.  A large value would probably be
        redundant given the number of similar things being cached
        """
        self._weights = {param : weights[param] for param in weights
                         if weights[param] != 0}
        if not self._weights and sanity_check:
            print("{} instantiated with no nonzero weights".format(type(self)),
                  file=sys.stderr)
        # note this is an instance property, cache included
        @functools.lru_cache(cache_size)
        def _evaluate(board):
            # return +/- infinity if the game is over
            if board.count_friends() == 0:
                return -inf
            elif board.count_foes() == 0:
                return inf
            return sum(weights[param] * getattr(board, param)()
                       for param in self._weights)
        self._evaluate = _evaluate

    def __call__(self, board):
        return self._evaluate(board)

def alphabeta_search(node, player, weights):
    ## Simple alpha-beta minimax search
    ## Stats out of 10 games, depth = 4:
    ##   9w:1d:0l
    ##   avg=  25.403s
    ##   max= 124.753s
    ##   min=   6.533s
    # return alphabeta(node, depth=4, alpha=-inf, beta=inf, maximum=True)

    ## Improved alpha-beta minimax search?
    return alphabeta_dfs(node, player, weights, depth=2, alpha=-inf, beta=inf,
                  maximum=True, cache=None, evaluator=eval)

    ## Iterative deepening using informed move order in deeper searches
    ## Stats out of 10 games, start_depth=2, end_depth=4:
    ##   9w:1d:0l
    ##   avg=  14.606s
    ##   max=  38.865s
    ##   min=   9.277s
    # return alphabeta_iterative_search(node, 4, 6)


#     ## Iterative deepening using informed move order in deeper searches
#     ## Stats out of 10 games, start_depth=2, end_depth=4:
#     ##   9w:1d:0l
#     ##   avg=  14.606s
#     ##   max=  38.865s
#     ##   min=   9.277s
#     return alphabeta_iterative_search(node, 4, 6)

# def alphabeta_iterative_search(node, start_depth, end_depth):
#     actions = node.actions()
#     for i in range(start_depth, end_depth+1):
#         score_action = alphabeta_iterative_deepening(node, actions, i)
#         if (i < end_depth):
#             actions = []
#             while not score_action[1].empty():
#                 s_act = score_action[1].get()
#                 if s_act[1]:
#                     actions.insert(0, s_act[1])

#     return score_action[0]

# def alphabeta_iterative_deepening(node, actions, depth=7, alpha=-inf, beta=inf, maximum=True):
#     """Returns a tuple (val, q), where:
#         - val is the return value of the total alphabeta search
#         - q is a priority queue of tuples: (score, action), for each action in actions ordered by lowest score first
#     """
#     # TODO make unit tests for this

#     if depth == 0 or node.terminal():
#         ret = queue.PriorityQueue()
#         ret.put((eval(node), None))
#         return (eval(node), ret)

#     ordered_actions = queue.PriorityQueue()

#     if maximum:
#         val = -inf
#         choose = max
#     else:
#         val = inf
#         choose = min
#     actions = node.list_actions()
#     for i in range(len(actions)):
#         action = actions[i]
#         child = node.result(action)
#         val = choose(val, alphabeta(child, depth=(depth-1), alpha=alpha,
#                                     beta=beta, maximum=(not maximum)))
#         ordered_actions.put((val, action))
#         if maximum:
#             alpha = choose(alpha, val)
#         else:
#             beta = choose(beta, val)
#         # Shouldn't ever be reached:
#         if beta <= alpha:
#             for act in actions[(i+1):]:
#                 ordered_actions.put((-inf, act))
#             break
#     return (val, ordered_actions)

# SearchCacheEntry = namedtuple("SearchCacheEntry",
#                               ("board", "maximum",
#                                # Note: if alpha/beta are as received as parameters,
#                                # don't cache them.  ... i think just val needed?
#                                # "alpha"=None, "beta"=None, # also bad syntax here
#                                "val",  # not a guaranteed value but a value for AB pruning
#                                "depth"))


def alphabeta_dfs(node, player, weights, depth=7, alpha=-inf, beta=inf,
                  maximum=True, cache=None, evaluator=None):
    """This is a work in progress. Beware. Committed at 2 AM."""
    if cache and (node, maximum) in cache:
        entry = cache[(node, maximum)]
        if entry.depth <= depth:
            entry = None  # This could be omitted for more zealous pruning
    else:
        entry = None
    # cache_alpha = None
    # cache_beta = None  # we shouldn't cache alpha/beta values computed above
    # this node of the search tree

    # TODO make unit tests for this
    if depth == 0 or node.count_friends() == 0 or node.count_foes() == 0:
        return evaluator(node, player, weights)
    if maximum:
        val = entry.val if entry else -inf
        choose = max
    else:
        val = entry.val if entry else inf
        choose = min
    for action in node.actions():
        if beta <= alpha:
            break
        child = node.result(action)
        val = choose(val, alphabeta_dfs(child, player, weights, depth=(depth-1), alpha=alpha,
                                        beta=beta, maximum=(not maximum),
                                        cache=cache, evaluator=evaluator))
        if maximum:
            alpha = choose(alpha, val)
            # if cache_alpha
        else:
            beta = choose(beta, val)

    # I guess cache val as either alpha or beta, no?
    return val
