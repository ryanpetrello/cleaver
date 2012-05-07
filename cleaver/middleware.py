from .base import Cleaver
from .backend import CleaverBackend
from .identity import CleaverIdentityProvider


class SplitMiddleware(object):

    def __init__(self, app, identity, backend, environ_key='cleaver'):
        """
        Makes a Cleaver instance available every request under
        ``environ['cleaver']``.

        :param identity any implementation of
                          ``identity.CleaverIdentityProvider`` or
                          a callable that emulates
                          ``identity.CleaverIdentityProvider.get_identity``.
        :param backend any implementation of
                            ``cleaver.backend.CleaverBackend``
        :param environ_key location where the Cleaver instance will be keyed in
                            the WSGI environ
        """
        self.app = app

        if not isinstance(identity, CleaverIdentityProvider) and \
            not callable(identity):
            raise RuntimeError(
                '%s must be callable or implement ' \
                    'cleaver.identity.CleaverIdentityProvider' % identity
            )
        if not isinstance(backend, CleaverBackend):
            raise RuntimeError(
                '%s must implement cleaver.backend.CleaverBackend' % backend
            )

        self._identity = identity
        self._backend = backend
        self.environ_key = environ_key

    def __call__(self, environ, start_response):
        environ[self.environ_key] = Cleaver(
            environ,
            self._identity,
            self._backend
        ).split
        return self.app(environ, start_response)
