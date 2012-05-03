import abc


class CleaverIdentityProvider(object):
    """
    Used to identify a user over a browsing session.
    """

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_identity(self):
        return  # pragma: nocover
