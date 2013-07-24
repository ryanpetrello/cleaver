import math

from .compat import string_types

__all__ = ['Experiment', 'VariantStat']


def _memoize(function):
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
        """
        The control (first alternative) for this experiment.

        Returns a string.
        """
        return self.variants[0]

    @property
    def participants(self):
        """
        The number of participants in this experiment.

        Returns a > 0 integer.
        """
        return sum(
            self.participants_for(v) for v in self.variants
        )

    @property
    def conversions(self):
        """
        The number of conversions in this experiment.

        Returns a > 0 integer.
        """
        return sum(
            self.conversions_for(v) for v in self.variants
        )

    @_memoize
    def participants_for(self, variant):
        """
        The number of participants for a certain variant of this experiment.

        Returns a > 0 integer.
        """
        return self.backend.participants(self.name, variant)

    @_memoize
    def conversions_for(self, variant):
        """
        The number of conversions for a certain variant of this experiment.

        Returns a > 0 integer.
        """
        return self.backend.conversions(self.name, variant)

    @classmethod
    def all(cls, backend):
        """
        A list of every existing Experiment.
        """
        return backend.all_experiments()

    def __repr__(self):
        return 'Experiment: %s <%s>' % (self.name, '|'.join(
            v for v in self.variants
        ))


class VariantStat(object):
    """
    Used to calculate statistics related to Experiment variants.
    """

    def __init__(self, name, experiment):
        self.name = name
        self.experiment = experiment

    @property
    def participant_count(self):
        """
        The number of participants for this variant.

        Returns a > 0 integer.
        """
        return self.experiment.participants_for(self.name)

    @property
    def conversion_rate(self):
        """
        The percentage of participants that have converted for this variant.

        Returns a > 0 float representing a percentage rate.
        """
        participants = self.participant_count
        if participants == 0:
            return 0.0
        return self.experiment.conversions_for(self.name) / float(participants)

    @property
    def z_score(self):
        """
        Calculate the Z-Score between this alternative and the project control.

        Statistical formulas based on:
        http://20bits.com/article/statistical-analysis-and-ab-testing
        """
        control = VariantStat(self.experiment.control, self.experiment)

        alternative = self

        if control.name == alternative.name:
            return 'N/A'

        conv_c = control.conversion_rate
        conv_a = alternative.conversion_rate

        num_c = control.participant_count
        num_a = alternative.participant_count

        if conv_c == 0 or conv_a == 0:
            return 0

        numerator = conv_a - conv_c

        frac_c = (conv_c * (1 - conv_c)) / float(num_c)
        frac_a = (conv_a * (1 - conv_a)) / float(num_a)

        if frac_c + frac_a == 0:
            # square root of 0 is 0, so no need to calculate
            return 0
        elif frac_c + frac_a < 0:
            # can't take a square root of a negative number,
            # so return 'Invalid'
            return 'Invalid'

        return numerator / math.sqrt((frac_c + frac_a))

    @property
    def confidence_level(self):
        """
        Based on the variant's Z-Score, returns a human-readable string that
        describes the confidence with which we can say the results are
        statistically significant.
        """
        z = self.z_score
        if isinstance(z, string_types):
            return z

        z = abs(round(z, 3))

        if z == 0.0:
            return "No Change"
        elif z < 1.65:
            return "No Confidence"
        elif z < 2.33:
            return "95% Confidence"
        elif z < 3.08:
            return "99% Confidence"
        return "99.9% Confidence"
