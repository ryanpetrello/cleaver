from unittest import TestCase
from datetime import datetime
from wsgiref.validate import validator
from wsgiref.util import setup_testing_defaults

from cleaver.experiment import Experiment
from cleaver.tests import FakeBackend
from cleaver.reports.web import CleaverWebUI


class SampleBackend(FakeBackend):

    def all_experiments(self):
        return [
            Experiment(
                self,
                'show_promo',
                datetime.utcnow(),
                ['True', 'False']
            )
        ]

    def participants(self, *args):
        return 0

    def conversions(self, *args):
        return 0


class TestWebUI(TestCase):

    def test_backend_required(self):
        self.assertRaises(
            RuntimeError,
            CleaverWebUI,
            None
        )

    def test_functional(self):
        app = validator(CleaverWebUI(SampleBackend()))

        environ = {}
        setup_testing_defaults(environ)

        environ['PATH_INFO'] = '/'
        environ['REQUEST_METHOD'] = 'GET'
        environ['QUERY_STRING'] = ''

        result = {}

        def start_response(status, headers):
            result['status'] = status

        resp = app(environ, start_response)
        assert result['status'] == '200 OK'

        if hasattr(resp, 'close'):
            resp.close()
            del resp
