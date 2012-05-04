from random import choice


class Experiment(object):

    def __init__(self, backend, name, started_on, variants):
        self.backend = backend
        self.name = name
        self.started_on = started_on
        self.variants = variants

    @property
    def participants(self):
        return sum(
            self.backend.participants(self.name, v) for v in self.variants
        )

    @property
    def conversions(self):
        return sum(
            self.backend.conversions(self.name, v) for v in self.variants
        )

    def random_variant(self, weights):
        return choice(self.variants)

    @property
    def winner(self):
        pass

    @classmethod
    def all(self, backend):
        backend.all_experiments()

    def __repr__(self):
        return 'Experiment: %s (%s)' % (self.name, ' | '.join(
            v for v in self.variants
        ))
