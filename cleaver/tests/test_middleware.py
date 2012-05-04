from unittest import TestCase
import inspect

from . import FakeIdentityProvider, FakeBackend
from cleaver import Cleaver, SplitMiddleware


class TestMiddleware(TestCase):

    @property
    def app(self):
        def a(environ, start_response):
            response_headers = [('Content-type', 'text/plain')]
            start_response('200 OK', response_headers)
            return ['Hello world!\n']
        return a

    def _make_request(self, **kw):
        environ = {}

        def start_response(status, response_headers, exc_info=None):
            self._status = status
            self._response_headers = response_headers

        SplitMiddleware(self.app, FakeIdentityProvider(), FakeBackend(), **kw)(
            environ,
            start_response
        )
        return environ

    def test_invalid_identity(self):
        self.assertRaises(
            RuntimeError,
            SplitMiddleware,
            self.app,
            None,
            FakeIdentityProvider()
        )

    def test_invalid_backend(self):
        self.assertRaises(
            RuntimeError,
            SplitMiddleware,
            self.app,
            FakeIdentityProvider(),
            None
        )

    def test_cleaver_in_environ(self):
        environ = self._make_request()
        assert 'cleaver' in environ
        assert inspect.ismethod(environ['cleaver'])
        assert environ['cleaver'].im_class is Cleaver

    def test_custom_environ_key(self):
        environ = self._make_request(environ_key='xyz')
        assert 'cleaver' not in environ
        assert 'xyz' in environ
        assert inspect.ismethod(environ['xyz'])
        assert environ['xyz'].im_class is Cleaver
