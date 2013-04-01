import tempfile
import cgi

from .base import Cleaver
from .compat import urlencode, parse_qsl
from .backend import CleaverBackend
from .identity import CleaverIdentityProvider


class SplitMiddleware(object):

    def __init__(self, app, identity, backend, environ_key='cleaver',
                 allow_override=False, count_humans_only=False,
                 human_callback_token='__cleaver_human_verification__'):
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
        :param count_humans_only when False, every request (including those
                                 originating from bots and web crawlers) is
                                 treated as a unique visit (defaults to False).
        :param human_callback_token when ``count_humans_only`` is True, this
                                    token in the URL will trigger a simple
                                    verification process for humans.
        """
        self.app = app

        if not isinstance(identity, CleaverIdentityProvider) and \
                not callable(identity):
            raise RuntimeError(
                '%s must be callable or implement '
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
        self.count_humans_only = count_humans_only
        self.human_callback_token = human_callback_token

    def __call__(self, environ, start_response):
        cleaver = Cleaver(
            environ,
            self._identity,
            self._backend,
            count_humans_only=self.count_humans_only
        )
        environ[self.environ_key] = cleaver

        if self.allow_override:
            self._handle_variant_overrides(environ)

        #
        # If human verification is required and this request represents
        # a valid AJAX callback (which bots aren't generally capable of), then
        # mark the visitor as human.
        #
        if self.count_humans_only and \
                environ.get('REQUEST_METHOD', '') == 'POST' and \
                self.human_callback_token in environ.get('PATH_INFO', ''):

            fp, length = SplitMiddleware._copy_body_to_tempfile(environ)
            environ.setdefault('CONTENT_LENGTH', length)

            fs = cgi.FieldStorage(
                fp=fp,
                environ=environ,
                keep_blank_values=True
            )

            try:
                try:
                    x = int(fs.getlist('x')[0])
                except (IndexError, ValueError):
                    x = 0
                try:
                    y = int(fs.getlist('y')[0])
                except (IndexError, ValueError):
                    y = 0
                try:
                    z = int(fs.getlist('z')[0])
                except (IndexError, ValueError):
                    z = 0

                # The AJAX call will include three POST arguments, X, Y, and Z
                #
                # Part of the "not a robot test" is validating that X + Y = Z
                # (most web crawlers won't perform complicated Javascript
                # execution like math and HTTP callbacks, because it's just too
                # expensive at scale)
                if x and y and z and x + y == z:
                    # Mark the visitor as a human
                    self._backend.mark_human(cleaver.identity)

                    # If the visitor has been assigned any experiment variants,
                    # tally their participation.
                    for e in self._backend.all_experiments():
                        variant = self._backend.get_variant(
                            cleaver.identity,
                            e.name
                        )
                        if variant:
                            self._backend.mark_participant(e.name, variant)

                    start_response(
                        '204 No Content',
                        [('Content-Type', 'text/plain')]
                    )
                    return []
            except (KeyError, ValueError):
                pass

            start_response(
                '401 Unauthorized',
                [('Content-Type', 'text/plain')]
            )
            return []

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

    @classmethod
    def _copy_body_to_tempfile(cls, environ):
        """
        Copy wsgi.input to a tempfile so it can be reused.
        """
        try:
            length = int(environ.get('CONTENT_LENGTH', 0))
        except ValueError:
            length = 0

        try:
            fileobj = tempfile.SpooledTemporaryFile(1024*1024)
        except AttributeError:  # pragma: nocover
            fileobj = tempfile.TemporaryFile()  # py25 fallback
        if length:
            remaining = length
            while remaining > 0:
                data = environ['wsgi.input'].read(min(remaining, 65536))
                if not data:
                    raise IOError(
                        "Client disconnected (%s more bytes were expected)"
                        % remaining
                    )
                fileobj.write(data)
                remaining -= len(data)

        fileobj.seek(0)
        environ['wsgi.input'] = fileobj
        return fileobj, length
