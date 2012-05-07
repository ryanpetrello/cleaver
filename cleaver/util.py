from random import randint
from bisect import bisect

__all__ = ['random_variant']


def random_variant(variants, weights):
    total = 0
    accumulator = []
    for w in weights:
        total += w
        accumulator.append(total)

    r = randint(0, total - 1)
    yield variants[bisect(accumulator, r)]
