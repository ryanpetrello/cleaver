from unittest import TestCase
import timeit

from cleaver.compat import next
from cleaver.util import random_variant


class TestRandomVariant(TestCase):

    def test_generally_random(self):
        items = ('True', 'False')
        weights = (1, 1)
        results = {}
        total = 50000

        for _ in range(total):
            v = next(random_variant(items, weights))
            results.setdefault(v, 0)
            results[v] += 1

        a = results['True'] / float(total)
        b = results['False'] / float(total)
        assert a > .49 and a < .51
        assert b > .49 and b < .51

    def test_generally_random_with_weights(self):
        items = ('A', 'B', 'C')
        weights = (1, 3, 6)
        results = {}
        total = 50000

        for _ in range(total):
            v = next(random_variant(items, weights))
            results.setdefault(v, 0)
            results[v] += 1

        a = results['A'] / float(total)
        b = results['B'] / float(total)
        c = results['C'] / float(total)
        assert a > .09 and a < .11
        assert b > .29 and b < .31
        assert c > .59 and c < .61

    def test_random_choice_speed(self):
        """
        Since it's potentially happening for each new visitor, weighted random
        choice should be very lightning fast for large numbers of variants
        *and* very large weights.
        """

        # Choose a random variant from 1K variants, each with a weight of 1M...
        elapsed = timeit.Timer(
            "next(random_variant(range(10000), repeat(1000000, 1000)))",
            "\n".join([
                "from cleaver.util import random_variant",
                "from cleaver.compat import next",
                "from itertools import repeat",
            ])
        ).timeit(1)

        #
        # ...and make sure it calculates within a thousandth of a second.
        # This boundary is completely non-scientific, isn't based on any
        # meaningful research, and it's possible that this test could fail on
        # especially old/slow hardware/platforms.
        #
        # The goal here isn't to assert some speed benchmark, but to prevent
        # changes to the selection algorithm that could decrease performance
        # in a significant way.
        #
        # The assumption is that a sufficiently slow/naive and
        # memory-inefficient algorithm, like the following:
        #
        # import random
        # from itertools import repeat
        #
        # def random_variant(weights):
        #     dist = []
        #     for v in weights.keys():
        #         dist += str(weights[v]) * v
        #
        #     return random.choice(dist)
        #
        # random_variant(dict(zip(range(10000), repeat(1000000))))
        #
        # ...would cause this test to fail.
        #
        assert elapsed < 0.01
