from unittest import TestCase
from itertools import cycle
from datetime import datetime
from wsgiref.util import setup_testing_defaults

from cleaver import SplitMiddleware
from cleaver.backend.redis import RedisBackend
from cleaver.compat import next
from cleaver.experiment import VariantStat


class TestFullStack(TestCase):

    def setUp(self):
        self.b = RedisBackend(prefix="testcleaver")

    def tearDown(self):
        for key in self.b.redis.keys("testcleaver:*"):
            self.b.redis.delete(key)

    def test_full_conversion(self):

        def _track(environ):
            return [environ['cleaver'](
                'Coin',
                ('Heads', 'Heads'),
                ('Tails', 'Tails')
            )]

        def _score(environ):
            environ['cleaver'].score('Coin')
            return []

        # Simulate an HTTP GET to track, and an HTTP POST later to convert
        handler = cycle((_track, _track, _score))

        def app(environ, start_response):
            response_headers = [('Content-type', 'text/plain')]
            start_response('200 OK', response_headers)
            return next(handler)(environ)

        environ = {}
        setup_testing_defaults(environ)

        app = SplitMiddleware(
            app,
            lambda environ: 'ryan',
            self.b
        )

        # The first request returns a variant and stores it
        variant = app(environ, lambda *args: None)[0]
        assert variant in ('Heads', 'Tails')

        assert len(self.b.all_experiments()) == 1
        assert self.b.all_experiments()[0].name == 'Coin'
        started_on = self.b.all_experiments()[0].started_on
        assert isinstance(started_on, datetime)

        experiment = self.b.get_experiment('Coin', ['Heads', 'Tails'])
        assert experiment.participants == 1
        assert self.b.participants('Coin', variant) == 1

        # The second request returns the same cleaver variant
        assert app(environ, lambda *args: None)[0] == variant

        assert len(self.b.all_experiments()) == 1
        assert self.b.all_experiments()[0].name == 'Coin'
        assert self.b.all_experiments()[0].started_on == started_on

        experiment = self.b.get_experiment('Coin', ['Heads', 'Tails'])
        assert experiment.participants == 1
        assert self.b.participants('Coin', variant) == 1

        # The third request marks a conversion
        assert app(environ, lambda *args: None) == []
        assert experiment.participants == 1
        assert experiment.conversions == 1
        assert self.b.conversions('Coin', variant) == 1

        assert VariantStat('Heads', experiment).z_score == 'N/A'
        assert VariantStat('Tails', experiment).z_score == 0

    def test_human_verification_required(self):

        def _track(environ):
            return [environ['cleaver'](
                'Coin',
                ('Heads', 'Heads'),
                ('Tails', 'Tails')
            )]

        def _score(environ):
            environ['cleaver'].score('Coin')
            return []

        # Simulate an HTTP GET to track, and an HTTP POST later to convert
        handler = cycle((_track, _score))

        def app(environ, start_response):
            response_headers = [('Content-type', 'text/plain')]
            start_response('200 OK', response_headers)
            return next(handler)(environ)

        environ = {}
        setup_testing_defaults(environ)

        app = SplitMiddleware(
            app,
            lambda environ: 'ryan',
            self.b,
            count_humans_only=True
        )

        # The first request returns a variant and stores it
        variant = app(environ, lambda *args: None)[0]
        assert variant in ('Heads', 'Tails')

        assert len(self.b.all_experiments()) == 1
        assert self.b.all_experiments()[0].name == 'Coin'
        started_on = self.b.all_experiments()[0].started_on
        assert isinstance(started_on, datetime)

        experiment = self.b.get_experiment('Coin', ['Heads', 'Tails'])
        assert experiment.participants == 0

        # The second request doesn't store the conversion
        # (because the visitor isn't verified as human)
        assert app(environ, lambda *args: None) == []

        assert experiment.conversions == 0
