import abc


class CleaverBackend(object):
    """
    Provides an interface for persisting and retrieving A/B test results, often
    a database or file on disk.
    """

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def save_test(self, test_name, variants):
        return

    @abc.abstractmethod
    def get_variant(self, identity, test_name):
        return

    @abc.abstractmethod
    def set_variant(self, identity, test_name, variant):
        return
