from unittest import TestCase
from wsgiref.util import setup_testing_defaults

from mock import Mock, patch, call

from . import FakeIdentityProvider, FakeBackend
from cleaver import Cleaver, SplitMiddleware
from cleaver.compat import urlencode, PY3


class TestMiddleware(TestCase):

    def setUp(self):
        self._resp = {}

    @property
    def app(self):
        def a(environ, start_response):
            response_headers = [('Content-type', 'text/plain')]
            start_response('200 OK', response_headers)
            return ['Hello world!\n']
        return a

    def _make_request(self, environ=None, postdata=None, **kw):
        environ = environ or {}
        setup_testing_defaults(environ)

        if postdata is not None:
            environ['REQUEST_METHOD'] = 'POST'
            if PY3:
                postdata = bytes(postdata, 'UTF-8')  # pragma: nocover
            environ['CONTENT_LENGTH'] = str(len(postdata))
            environ['wsgi.input'].write(postdata)
            environ['wsgi.input'].seek(0)

        def start_response(status, response_headers, exc_info=None):
            self._resp['status'] = status

        SplitMiddleware(self.app, lambda environ: 'ryan', FakeBackend(), **kw)(
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

    @patch.object(FakeBackend, 'mark_human')
    @patch.object(FakeBackend, 'all_experiments', lambda *args: [])
    def test_human_callback(self, mark_human):
        self._make_request({
            'PATH_INFO': '/__cleaver_human_verification__'
        }, postdata='x=1&y=2&z=3', count_humans_only=True)
        assert self._resp['status'] == '204 No Content'

        mark_human.assert_called_with('ryan')

    @patch.object(FakeBackend, 'mark_human')
    @patch.object(FakeBackend, 'mark_participant')
    @patch.object(FakeBackend, 'get_variant')
    @patch.object(FakeBackend, 'all_experiments')
    def test_callback_with_new_participants(self, all_experiments,
                                            get_variant, mark_participant,
                                            mark_human):

        first = Mock()
        first.name = 'show_promo'
        second = Mock()
        second.name = 'color'
        all_experiments.return_value = [
            first, second
        ]

        get_variant.side_effect = ['True', 'blue']

        self._make_request({
            'PATH_INFO': '/__cleaver_human_verification__'
        }, postdata='x=1&y=2&z=3', count_humans_only=True)
        assert self._resp['status'] == '204 No Content'

        mark_human.assert_called_with('ryan')
        get_variant.assert_has_calls([
            call('ryan', 'show_promo'),
            call('ryan', 'color'),
        ])
        mark_participant.assert_has_calls([
            call('show_promo', 'True'),
            call('color', 'blue'),
        ])

    def test_missing_input(self):
        self._make_request({
            'PATH_INFO': '/__cleaver_human_verification__'
        }, postdata='', count_humans_only=True)
        assert self._resp['status'] == '401 Unauthorized'

    def test_deformed_input(self):
        self._make_request({
            'PATH_INFO': '/__cleaver_human_verification__'
        }, postdata='rtoanrt98arst0larst', count_humans_only=True)
        assert self._resp['status'] == '401 Unauthorized'

    def test_missing_arguments(self):
        self._make_request({
            'PATH_INFO': '/__cleaver_human_verification__'
        }, postdata='x=5', count_humans_only=True)
        assert self._resp['status'] == '401 Unauthorized'

    def test_non_integer_arguments(self):
        self._make_request({
            'PATH_INFO': '/__cleaver_human_verification__'
        }, postdata='x=5&y=10&z=dog', count_humans_only=True)
        assert self._resp['status'] == '401 Unauthorized'

    def test_bad_math(self):
        self._make_request({
            'PATH_INFO': '/__cleaver_human_verification__'
        }, postdata='x=5&y=10&z=250', count_humans_only=True)
        assert self._resp['status'] == '401 Unauthorized'
