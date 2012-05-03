from random import choice
from .backend import CleaverBackend

__version__ = 0.1
__all__ = ['Cleaver']


class Cleaver(object):

    def __init__(self, environ, backend):
        """
        Create a new Cleaver instance.

        :param environ - the WSGI environ dictionary for the current request
        :param backend - any implementation of cleaver.CleaverBackend
        """

        if not isinstance(backend, CleaverBackend):
            raise RuntimeError(
                '%s must implement cleaver.backend.CleaverBackend' % backend
            )
        self.backend = backend

    @property
    def identity(self):
        return 'XYZ'

    def split(self, test_name, *variants):
        """
        Used to split and track user experience amongst one or more variants.

        :param *variants can take many forms, depending on usage.

            When no variants are provided, test variants fall back to a simple
            True/False 50/50 split, e.g.,

            >>> do_this() if split('include_sidebar') else do_that()

            Otherwise, variants should be provided as arbitrary tuples:

            >>> split('text_color', ('red', '#F00'), ('blue', '#00F'))

            By default, variants are chosen with equal weight.  You can tip the
            scales if you like by passing a proportional weight in each variant
            tuple:

            >>> split('text_color', ('red', '#F00', 2), ('blue', '#00F', 4))
        """
        variants, weights = self._parse_variants(**variants)

        self.backend.save_test(test_name, variants.keys())

        variant = self.backend.get_variant(self.identity, test_name)
        if variant is None:
            variant = self._choose(variants.keys(), variants)

        self.backend.set_variant(self.identity, test_name, variant)
        return variants[variant]

    def score(self, test_name):
        self.backend.score(test_name)

    def _parse_variants(self, variants):
        if not len(variants):
            variants = [('True', True), ('False', False)]

        weights = []
        for v in variants:
            try:
                weights.append(v[2])
            except IndexError:
                weights.append(1)

        variants = dict(v[:2] for v in variants)
        return variants, weights

    def _choose(self, variants, weights):
        return choice(variants)
