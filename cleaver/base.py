from random import choice
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict  # noqa

from .backend import CleaverBackend
from .identity import CleaverIdentityProvider


class Cleaver(object):

    def __init__(self, identity, backend):
        """
        Create a new Cleaver instance.

        :param identity - any implementation of
                            ``cleaver.identity.CleaverIdentityProvider``
        :param backend - any implementation of
                            ``cleaver.backend.CleaverBackend``
        """

        if not isinstance(identity, CleaverIdentityProvider):
            raise RuntimeError(
                '%s must implement cleaver.identity.CleaverIdentityProvider' \
                    % identity
            )
        if not isinstance(backend, CleaverBackend):
            raise RuntimeError(
                '%s must implement cleaver.backend.CleaverBackend' % backend
            )
        self._identity = identity
        self._backend = backend

    @property
    def identity(self):
        return self._identity.get_identity()

    def split(self, test_name, *variants):
        """
        Used to split and track user experience amongst one or more variants.

        :param *variants can take many forms, depending on usage.

            When no variants are provided, test variants fall back to a simple
            True/False 50/50 split, e.g.,

            >>> sidebar() if split('include_sidebar') else empty()

            Otherwise, variants should be provided as arbitrary tuples:

            >>> split('text_color', ('red', '#F00'), ('blue', '#00F'))

            By default, variants are chosen with equal weight.  You can tip the
            scales if you like by passing a proportional weight in each variant
            tuple:

            >>> split('text_color', ('red', '#F00', 2), ('blue', '#00F', 4))
        """
        variants, weights = self._parse_variants(variants)

        self._backend.save_test(test_name, variants.keys())

        variant = self._backend.get_variant(self.identity, test_name)
        if variant is None:
            variant = self._choose(variants.keys(), variants)
            self._backend.set_variant(self.identity, test_name, variant)

        return variants[variant]

    def score(self, test_name):
        self._backend.score(self.identity, test_name)

    def _parse_variants(self, variants):
        if not len(variants):
            variants = [('True', True), ('False', False)]

        weights = []
        for v in variants:
            try:
                weights.append(v[2])
            except IndexError:
                weights.append(1)

        variants = OrderedDict(v[:2] for v in variants)
        return variants, weights

    def _choose(self, variants, weights):
        return choice(variants)
