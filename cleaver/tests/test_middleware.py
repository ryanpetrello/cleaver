from unittest import TestCase
from wsgiref.util import setup_testing_defaults

from . import FakeIdentityProvider, FakeBackend
from cleaver import Cleaver, SplitMiddleware
from cleaver.compat import urlencode


class TestMiddleware(TestCase):

    @property
    def app(self):
        def a(environ, start_response):
            response_headers = [('Content-type', 'text/plain')]
            start_response('200 OK', response_headers)
            return ['Hello world!\n']
        return a

    def _make_request(self, environ=None, **kw):
        environ = environ or {}
        setup_testing_defaults(environ)

        def start_response(status, response_headers, exc_info=None):
            pass

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
        assert isinstance(environ['cleaver'], Cleaver)
        assert callable(environ['cleaver'])

    def test_custom_environ_key(self):
        environ = self._make_request(environ_key='xyz')
        assert 'cleaver' not in environ
        assert 'xyz' in environ
        assert isinstance(environ['xyz'], Cleaver)
        assert callable(environ['xyz'])

    def test_cleaver_override_disabled(self):
        environ = self._make_request({
            'QUERY_STRING': urlencode({
                'cleaver:show_promo': 'False'
            })
        })

        assert environ['QUERY_STRING'] == urlencode({
            'cleaver:show_promo': 'False'
        })
        assert 'cleaver.override' not in environ

    def test_cleaver_override_variable_consumption(self):
        environ = self._make_request({
            'QUERY_STRING': urlencode({
                'cleaver:show_promo': 'False'
            })
        }, allow_override=True)

        assert environ['QUERY_STRING'] == ''
        assert environ['cleaver.override'] == {
            'show_promo': 'False'
        }

    def test_cleaver_override_variable_consumption_with_colons(self):
        environ = self._make_request({
            'QUERY_STRING': urlencode({
                'cleaver:a:b': 'Yes'
            })
        }, allow_override=True)

        assert environ['QUERY_STRING'] == ''
        assert environ['cleaver.override'] == {
            'a:b': 'Yes'
        }

    def test_cleaver_override_with_multiple_variable_consumption(self):
        environ = self._make_request({
            'QUERY_STRING': urlencode({
                'cleaver:show_promo': 'False',
                'cleaver:Button Size': 'large'
            })
        }, allow_override=True)

        assert environ['QUERY_STRING'] == ''
        assert environ['cleaver.override'] == {
            'show_promo': 'False',
            'Button Size': 'large'
        }

    def test_cleaver_override_with_mixed_query_args(self):
        environ = self._make_request({
            'QUERY_STRING': urlencode({
                'cleaver:show_promo': 'False',
                'article': 25,
                'cleaver:Button Size': 'large'
            })
        }, allow_override=True)

        assert environ['QUERY_STRING'] == 'article=25'
        assert environ['cleaver.override'] == {
            'show_promo': 'False',
            'Button Size': 'large'
        }
