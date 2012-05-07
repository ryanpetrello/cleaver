class Experiment(object):
    """
    Represents an experiment record and related utilities.
    Not generally instantiated directly.

    :param backend an instance of ``cleaver.backend.CleaverBackend``.
    :param name a unique string identifier for the test
    :param started_on the date the first participant started the test
    :param variants a list of string variants
    """

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

    @property
    def winner(self):
        pass

    @classmethod
    def all(cls, backend):
        return backend.all_experiments()

    def __repr__(self):
        return 'Experiment: %s <%s>' % (self.name, '|'.join(
            v for v in self.variants
        ))
