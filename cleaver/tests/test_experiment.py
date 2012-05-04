from unittest import TestCase
from datetime import datetime

from mock import Mock

from cleaver.experiment import Experiment


class TestExperiment(TestCase):

    def test_participants(self):
        backend = Mock()
        backend.participants = lambda name, v: 50

        assert Experiment(
            backend,
            'show_promo',
            datetime.utcnow(),
            ['True', 'False']
        ).participants == 100

    def test_conversions(self):
        backend = Mock()
        backend.conversions = lambda name, v: 50

        assert Experiment(
            backend,
            'show_promo',
            datetime.utcnow(),
            ['True', 'False']
        ).conversions == 100

    def test_all(self):
        backend = Mock()
        backend.all_experiments = lambda: [Mock(), Mock(), Mock()]

        assert len(Experiment.all(backend)) == 3

    def test_rep(self):
        assert repr(Experiment(
            Mock(),
            'show_promo',
            datetime.utcnow(),
            ['True', 'False']
        )) == 'Experiment: show_promo <True|False>'
