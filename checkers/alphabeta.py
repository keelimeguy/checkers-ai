#!/usr/bin/env python3

import pylru  # lru cache in pure python

try:
    from math import inf
except ImportError:
    inf = float('inf')

from collections import namedtuple

class AlphaBeta(object):
    # __metaclass__ = abc.ABCMeta

    def __init__(self, heuristic, cache_size=(65536*8), default_depth=7):
        self.heuristic_eval = heuristic  # function to evaluate search nodes
        self.cache = pylru.lrucache(cache_size)
        if default_depth is not None:  # 0 is valid, so check for None explicitly
            self.default_depth = default_depth

    SearchCacheEntry = namedtuple("SearchCacheEntry",
                                  ("val",  # note because of pruning the
                                   #  guarantees for this return value are weak.
                                   "depth"))


    # accept cache entries from searches of depth cache_quality_fudge less than
    # the current depth requirement:
    cache_quality_fudge = 0  # experiment with this.  It could just be terrible

    def ab_dfs(self, node, depth=None, alpha=-inf, beta=inf, maximum=True,
               side_effect=None):
        """Alpha beta DFS from the given node and return its value.
        If cache_quality_fudge is greater than zero, the answer is not
        guaranteed correct.
        """

        if side_effect is not None:
            side_effect()  # used to throw StopPrecomputation, for instance

        if depth is None:
            depth = self.default_depth
        gamma = alpha if maximum else beta  # one variable for "the relevant thing"
        choice = max if maximum else min
        sign = 1 if maximum else -1
        # val = gamma
        if maximum:
            def finished():  # gamma is alpha
                return gamma >= beta
        else:
            def finished():  # gamma is beta
                return alpha >= gamma

        def recur(child, gamma):
            return self.ab_dfs(child, depth=(depth - 1),
                               alpha=(gamma if maximum else alpha),
                               beta=(beta if maximum else gamma),
                               maximum=(not maximum))

        # check the cache to see if we can prune extra
        # ca = self.cache[(node, maximum)]
        if (node, maximum) in self.cache:
            ca = self.cache[(node, maximum)]
            if ca.depth + self.cache_quality_fudge >= depth:
                gamma = choice(gamma, ca.val)  # bonkers
                if finished() or gamma in {-inf, inf}:
                    # +/- inf in cache means somebody wins for real.
                    #  self.cache.touch((node, maximum)) # redundant (idea was
                    #  to mark value as recently used (without changing it,
                    #  *especially* to reflect the current search depth!))
                    return gamma
        # base case, finally.
        if depth <= 0  or not node.count_friends() or not node.count_foes():
            # return choice(gamma, self.heuristic_eval(node) * sign)
            # Note: this checks if the node is terminal (and returns +/- inf)
            return self.heuristic_eval(node) * sign

        # iterate through actions sorted from bestest to worstest
        for new_state in sorted((node.result(act) for act in node.actions()),
                                key=(lambda m: sign * self.heuristic_eval(m))):
            if finished():
                # return val
                break  # prune away the rest of the search
            gamma = choice(gamma, recur(new_state, gamma))

        if finished() or gamma in {-inf, inf}:
            self.cache[(node, maximum)] = self.SearchCacheEntry(
                val=gamma, depth=depth)
        return gamma
