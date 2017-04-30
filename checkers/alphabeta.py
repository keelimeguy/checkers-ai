#!/usr/bin/env python3

# import abc
from math import inf
import pylru  # lru cache in pure python

def AlphaBeta(object):
    # __metaclass__ = abc.ABCMeta

    def __init__(self, heuristic, cache_size=10001):
        self.heuristic_eval = heuristic  # function to evaluate search nodes
        self.cache = pylru.lrucache(cache_size)

    SearchCacheEntry = namedtuple("SearchCacheEntry",
                                  ("val",  # note because of pruning the
                                   #  guarantees for this return value are weak.
                                   "depth"))


    default_depth = 7
    # accept cache entries from searches of depth cache_quality_fudge less than
    # the current depth requirement:
    cache_quality_fudge = 2  # experiment with this.  It could just be terrible

    def ab_dfs(self, node, depth=None, alpha=-inf, beta=inf, maximum=True):
        """Alpha beta DFS from the given node and return its value.

        If cache_quality_fudge is greater than zero, the answer is not
        guaranteed correct.
        """
        depth = depth or self.default_depth
        gamma = alpha if maximum else beta  # one variable for "the relevant thing"
        choice = max if maximum else min
        sign = 1 if maximum else -1
        # val = gamma
        if depth <= 0:
            return self.heuristic_eval(node) * sign
        if maximum:
            def finished():  # gamma is alpha
                return gamma <= beta
        else:
            def finished():  # gamma is beta
                return alpha <= gamma

        def recur(child, gamma):
            return self.ab_dfs(child, depth=(depth - 1),
                               alpha=(gamma if maximum else alpha),
                               beta=(beta if maximum else gamma),
                               maximum=(not maximum))

        # check the cache to see if we can prune extra
        ca = self.cache[(node, maximum)]
        if (node, maximum) in self.cache:
            ca = self.cache[(node, maximum)]
            if ca.depth + self.cache_quality_fudge >= self.depth:
                gamma = choice(gamma, ca.val)
                if finished():
                    #  self.cache.touch((node, maximum)) # redundant (idea was
                    #  to mark value as recently used (without changing it,
                    #  *especially* to reflect the current search depth!))
                    return gamma

        # iterate through actions sorted from bestest to worstest
        for new_state in sorted(node.result(act) for act in node.actions(),
                                key=(lambda m: sign * self.heuristic_eval(m))):
            if finished():
                # return val
                break  # prune away the rest of the search
            gamma = choice(gamma, recur(new_state, gamma))

        self.cache[(node, maximum)] = self.SearchCacheEntry(val=gamma,
                                                            depth=depth)
        return gamma
