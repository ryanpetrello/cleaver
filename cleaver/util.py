from random import randint
from bisect import bisect

__all__ = ['random_variant']


def random_variant(variants, weights):
    """
    A generator that, given a list of variants and a corresponding list of
    weights, returns one random weighted selection.
    """
    total = 0
    accumulator = []
    for w in weights:
        total += w
        accumulator.append(total)

    r = randint(0, total - 1)
    yield variants[bisect(accumulator, r)]
