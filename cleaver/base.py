from itertools import izip_longest

from .backend import CleaverBackend
from .identity import CleaverIdentityProvider


class Cleaver(object):

    def __init__(self, identity, backend):
        """
        Create a new Cleaver instance.

        Not generally instantiated directly, but established automatically by
        ``cleaver.SplitMiddleware`` and used within a WSGI application via
        ``request.environ['cleaver']``.

        :param identity any implementation of
                          ``cleaver.identity.CleaverIdentityProvider``
        :param backend any implementation of
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

    def split(self, experiment_name, *variants):
        """
        Used to split and track user experience amongst one or more variants.

        :param *variants can take many forms, depending on usage.

            When no variants are provided, the test falls back to a simple
            True/False 50/50 split, e.g.,

            >>> sidebar() if split('include_sidebar') else empty()

            Otherwise, variants should be provided as arbitrary tuples:

            >>> split('text_color', ('red', '#F00'), ('blue', '#00F'))

            By default, variants are chosen with equal weight.  You can tip the
            scales if you like by passing a proportional weight in each variant
            tuple:

            >>> split('text_color', ('red', '#F00', 2), ('blue', '#00F', 4))
        """
        keys, values, weights = self._parse_variants(variants)
        b = self._backend

        # Record the experiment if it doesn't exist already
        experiment = b.get_experiment(experiment_name, keys) or \
            b.save_experiment(experiment_name, keys)

        # Retrieve the variant assigned to the current user
        variant = b.get_variant(self.identity, experiment.name)
        if variant is None:
            # ...or choose (and store) one randomly if it doesn't exist yet...
            variant = experiment.random_variant(weights)
            b.participate(self.identity, experiment.name, variant)

        return dict(zip(keys, values))[variant]

    def score(self, experiment_name):
        """
        Used to mark the current experiment variant as "converted".

        :param experiment_name the string name of the experiment
        """
        self._backend.score(
            experiment_name,
            self._backend.get_variant(self.identity, experiment_name)
        )

    def _parse_variants(self, variants):
        if not len(variants):
            variants = [('True', True), ('False', False)]

        variants = map(
            lambda v: tuple(list(v) + [1]) if len(v) < 3 else v,
            variants
        )

        return izip_longest(*variants)
