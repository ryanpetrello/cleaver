try:
    import abc
except ImportError:  # pragma: nocover
    from cleaver.compat import abc  # noqa


class CleaverBackend(object):
    """
    Provides an interface for persisting and retrieving A/B test results,
    generally a database, cache, or file on disk.

    Generally speaking, base implementations need to:

        * Provide a list of all experiments and the datetime they started.
        * Save and retrieve an experiment and its ordered list of variants.
        * Save and retrieve a mapping between unique user identifiers and
          experiment/variant pairs those users were served.
        * Remember whether a certain unique visitor has been verified as
          a human (defaulting to False to prevent robots from skewing
          reporting).
        * Provide the ability to score a conversion for a certain (experiment,
          variant) pair.
        * Provide a running tally of participants and conversions for any
          (experiment, variant) pair.
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

        Variants should be stored in such a way that *order can be guaranteed*
        on retrieval.

        :param name a unique string name for the experiment
        :param variants a list of strings, each with a unique variant name
        """
        return  # pragma: nocover

    @abc.abstractmethod
    def is_verified_human(self, identity):
        return  # pragma: nocover

    @abc.abstractmethod
    def mark_human(self, identity):
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
    def set_variant(self, identity, experiment_name, variant):
        """
        Set the variant for a specific user.

        :param identity a unique user identifier
        :param experiment_name the string name of the experiment
        :param variant the string name of the variant
        """
        return  # pragma: nocover

    @abc.abstractmethod
    def mark_participant(self, experiment_name, variant):
        """
        Mark a participation for a specific experiment variant.

        :param experiment_name the string name of the experiment
        :param variant the string name of the variant
        """
        return  # pragma: nocover

    def participate(self, identity, experiment_name, variant):
        """
        Set the variant for a specific user and mark a participation for the
        experiment.

        Participation will *only* be marked for visitors who have been verified
        as humans (to avoid skewing reports with requests from bots and web
        crawlers).
        """
        self.set_variant(identity, experiment_name, variant)
        if self.is_verified_human(identity):
            self.mark_participant(experiment_name, variant)

    @abc.abstractmethod
    def mark_conversion(self, experiment_name, variant):
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
