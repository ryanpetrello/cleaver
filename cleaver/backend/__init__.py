import abc


class CleaverBackend(object):
    """
    Provides an interface for persisting and retrieving A/B test results,
    generally a database or file on disk.
    """

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def all_experiments(self):
        """
        Retrieve every available experiment.

        Returns a list of ``cleaver.experiment.Experiment``s
        """
        return  # pragma: nocover

    @abc.abstractmethod
    def get_experiment(self, name, variants):
        """
        Retrieve an experiment by its name and variants (assuming it exists).

        :param name a unique string name for the experiment
        :param variants a list of strings, each with a unique variant name

        Returns a ``cleaver.experiment.Experiment`` or ``None``
        """
        return  # pragma: nocover

    @abc.abstractmethod
    def save_experiment(self, name, variants):
        """
        Persist an experiment and its variants (unless they already exist).

        :param name a unique string name for the experiment
        :param variants a list of strings, each with a unique variant name
        """
        return  # pragma: nocover

    @abc.abstractmethod
    def get_variant(self, identity, experiment_name):
        """
        Retrieve the variant for a specific user and experiment (if it exists).

        :param identity a unique user identifier
        :param experiment_name the string name of the experiment

        Returns a ``String`` or `None`
        """
        return  # pragma: nocover

    @abc.abstractmethod
    def participate(self, identity, experiment_name, variant):
        """
        Set the variant for a specific user and mark a participation for the
        experiment.

        :param identity a unique user identifier
        :param experiment_name the string name of the experiment
        :param variant the string name of the variant
        """
        return  # pragma: nocover

    @abc.abstractmethod
    def score(self, experiment_name, variant):
        """
        Mark a conversion for a specific experiment variant.

        :param experiment_name the string name of the experiment
        :param variant the string name of the variant
        """
        return  # pragma: nocover

    @abc.abstractmethod
    def participants(self, experiment_name, variant):
        """
        The number of participants for a certain variant.

        Returns an integer.
        """
        return  # pragma: nocover

    @abc.abstractmethod
    def conversions(self, experiment_name, variant):
        """
        The number of conversions for a certain variant.

        Returns an integer.
        """
        return  # pragma: nocover
