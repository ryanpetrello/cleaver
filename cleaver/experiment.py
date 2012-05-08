import math


def memoize(function):
    cache = {}

    def decorated(*args):
        if args not in cache:
            cache[args] = function(*args)
        return cache[args]
    return decorated


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
    def control(self):
        return self.variants[0]

    @property
    def participants(self):
        return sum(
            self.participants_for(v) for v in self.variants
        )

    @property
    def conversions(self):
        return sum(
            self.conversions_for(v) for v in self.variants
        )

    @memoize
    def participants_for(self, variant):
        return self.backend.participants(self.name, variant)

    @memoize
    def conversions_for(self, variant):
        return self.backend.conversions(self.name, variant)

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


class VariantStat(object):

    def __init__(self, name, experiment):
        self.name = name
        self.experiment = experiment

    @property
    def participant_count(self):
        return self.experiment.participants_for(self.name)

    @property
    def conversion_rate(self):
        participants = self.participant_count
        if participants == 0:
            return 0.0
        return self.experiment.conversions_for(self.name) / float(participants)

    @property
    def z_score(self):
        """
        Calculate the Z-Score between this alternative and the project control.

        See:
        http://20bits.com/article/statistical-analysis-and-ab-testing
        """
        control = VariantStat(self.experiment.control, self.experiment)

        alternative = self

        if control.name == alternative.name:
            return 'N/A'

        conv_c = control.conversion_rate
        conv_a = alternative.conversion_rate

        c = control.participant_count
        a = alternative.participant_count

        if conv_c == 0:
            return 0

        z = conv_a - conv_c
        s = (conv_a * (1 - conv_a)) / a + (conv_c * (1 - conv_c)) / c
        return z / math.sqrt(s)

    @property
    def confidence_level(self):
        z = self.z_score
        if isinstance(z, basestring):
            return z

        z = abs(round(z, 3))

        if z == 0.0:
            return "No Change"
        elif z < 1.65:
            return "No Confident"
        elif z < 2.33:
            return "95% Confident"
        elif z < 3.08:
            return "99% Concident"
        return "99.9% Confident"
