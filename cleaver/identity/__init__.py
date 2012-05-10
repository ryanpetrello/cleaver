try:
    import abc
except ImportError:  # pragma: nocover
    from cleaver.compat import abc  # noqa


class CleaverIdentityProvider(object):
    """
    Used to identify a user over a browsing session.
    """

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_identity(self, environ):
        return  # pragma: nocover
