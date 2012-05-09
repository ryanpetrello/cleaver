from .base import Cleaver
from .compat import urlencode, parse_qsl
from .backend import CleaverBackend
from .identity import CleaverIdentityProvider


class SplitMiddleware(object):

    def __init__(self, app, identity, backend, environ_key='cleaver',
            allow_override=False, require_human_verification=False):
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
        :param allow_override when True, specific variants can be overriden via
                              the request query string, e.g.,

                              http://mypythonapp.com?cleaver:button_size=small

                              Especially useful for tests and QA.
        :param require_human_verification When False, every request (including
                                          those originating from bots and web
                                          crawlers) is treated as a unique
                                          visit (defaults to False).
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
        self.allow_override = allow_override
        self.require_human_verification = require_human_verification

    def __call__(self, environ, start_response):
        environ[self.environ_key] = Cleaver(
            environ,
            self._identity,
            self._backend,
            require_human_verification=self.require_human_verification
        ).split

        if self.allow_override:
            self._handle_variant_overrides(environ)

        return self.app(environ, start_response)

    def _handle_variant_overrides(self, environ):
        # Parse the QUERY_STRING into a dictionary, and make an editable copy
        parsed = dict(parse_qsl(environ.get('QUERY_STRING', '')))
        qs = parsed.copy()

        # For each key that starts with cleaver: ...
        for k in parsed:
            if k.startswith('cleaver:'):
                # Store the key -> value in ``environ['cleaver.override']``
                # and remove it from the editable ``qs`` copy.
                environ.setdefault('cleaver.override', {})[
                    k.split('cleaver:')[1]
                ] = qs.pop(k)

        # If any overriden variables were changed, re-encode QUERY_STRING so
        # that the next WSGI layer doesn't see the parsed ``cleaver:``
        # arguments.
        if 'cleaver.override' in environ:
            environ['QUERY_STRING'] = urlencode(qs)
