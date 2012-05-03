import abc


class CleaverBackend(object):
    """
    Provides an interface for persisting and retrieving A/B test results,
    generally a database or file on disk.
    """

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def save_test(self, test_name, variants):
        """
        Persist a test and its variants (unless they already exist).
        """
        return  # pragma: nocover

    @abc.abstractmethod
    def get_variant(self, identity, test_name):
        """
        Retrieve the test variant for a specific user (if it exists).
        """
        return  # pragma: nocover

    @abc.abstractmethod
    def set_variant(self, identity, test_name, variant):
        """
        Set the test variant for a specific user.
        """
        return  # pragma: nocover

    @abc.abstractmethod
    def score(self, identity, test_name):
        """
        Mark a specific user as "converted" for a certain test.
        """
        return  # pragma: nocover
