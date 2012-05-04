from unittest import TestCase
from datetime import datetime

from mock import patch

from cleaver import Cleaver
from cleaver.experiment import Experiment
from cleaver.identity import CleaverIdentityProvider
from cleaver.backend import CleaverBackend


class FakeIdentityProvider(CleaverIdentityProvider):

    def get_identity(self):
        pass  # pragma: nocover


class FakeBackend(CleaverBackend):

    def all_experiments(self):
        pass  # pragma: nocover

    def get_experiment(self, name, variants):
        pass  # pragma: nocover

    def save_experiment(self, name, variants):
        pass  # pragma: nocover

    def get_variant(self, identity, experiment_name):
        pass  # pragma: nocover

    def participate(self, identity, experiment_name, variant):
        pass  # pragma: nocover

    def score(self, experiment_name, variant):
        pass  # pragma: nocover

    def participants(self, experiment_name, variant):
        pass  # pragma: nocover

    def conversions(self, experiment_name, variant):
        pass  # pragma: nocover


class TestBase(TestCase):

    def test_valid_configuration(self):
        cleaver = Cleaver(FakeIdentityProvider(), FakeBackend())
        assert isinstance(cleaver._identity, FakeIdentityProvider)
        assert isinstance(cleaver._backend, FakeBackend)

    def test_invalid_identity(self):
        self.assertRaises(RuntimeError, Cleaver, None, FakeIdentityProvider())

    def test_invalid_backend(self):
        self.assertRaises(RuntimeError, Cleaver, FakeIdentityProvider(), None)

    @patch.object(FakeIdentityProvider, 'get_identity')
    def test_identity(self, get_identity):
        cleaver = Cleaver(FakeIdentityProvider(), FakeBackend())
        get_identity.return_value = 'ABC123'

        assert cleaver.identity == 'ABC123'


class TestSplit(TestCase):

    @patch.object(FakeBackend, 'get_experiment')
    @patch.object(FakeBackend, 'save_experiment')
    def test_experiment_save(self, save_experiment, get_experiment):
        backend = FakeBackend()
        get_experiment.return_value = None
        save_experiment.return_value = Experiment(
            backend=backend,
            name='show_promo',
            started_on=datetime.utcnow(),
            variants=['True', 'False']
        )
        cleaver = Cleaver(FakeIdentityProvider(), backend)

        assert cleaver.split('show_promo') in (True, False)
        get_experiment.assert_called_with('show_promo', ('True', 'False'))
        save_experiment.assert_called_with('show_promo', ('True', 'False'))

    @patch.object(FakeBackend, 'get_experiment')
    def test_experiment_get(self, get_experiment):
        backend = FakeBackend()
        get_experiment.return_value = Experiment(
            backend=backend,
            name='show_promo',
            started_on=datetime.utcnow(),
            variants=['True', 'False']
        )
        cleaver = Cleaver(FakeIdentityProvider(), backend)

        assert cleaver.split('show_promo') in (True, False)
        get_experiment.assert_called_with('show_promo', ('True', 'False'))

    @patch.object(FakeBackend, 'get_experiment')
    @patch.object(FakeBackend, 'participate')
    @patch.object(FakeIdentityProvider, 'get_identity')
    def test_variant_participation(self, get_identity, participate,
            get_experiment):
        cleaver = Cleaver(FakeIdentityProvider(), FakeBackend())
        get_experiment.return_value.name = 'show_promo'
        get_experiment.return_value.random_variant.return_value = 'True'
        get_identity.return_value = 'ABC123'

        assert cleaver.split('show_promo') in (True, False)
        participate.assert_called_with('ABC123', 'show_promo', 'True')

    @patch.object(FakeBackend, 'score')
    @patch.object(FakeBackend, 'get_variant')
    @patch.object(FakeIdentityProvider, 'get_identity')
    def test_score(self, get_identity, get_variant, score):
        cleaver = Cleaver(FakeIdentityProvider(), FakeBackend())
        get_variant.return_value = 'red'
        get_identity.return_value = 'ABC123'

        cleaver.score('primary_color')
        score.assert_called_with('primary_color', 'red')


class TestVariants(TestCase):

    def test_true_false(self):
        c = Cleaver(FakeIdentityProvider(), FakeBackend())
        assert tuple(c._parse_variants([])) == (
            ('True', 'False'),
            (True, False),
            (1, 1)
        )

    def test_a_b(self):
        c = Cleaver(FakeIdentityProvider(), FakeBackend())
        assert tuple(c._parse_variants([
            ('red', '#F00'), ('green', '#0F0')
        ])) == (
            ('red', 'green'),
            ('#F00', '#0F0'),
            (1, 1)
        )

    def test_multivariate(self):
        c = Cleaver(FakeIdentityProvider(), FakeBackend())
        assert tuple(c._parse_variants([
            ('red', '#F00'), ('green', '#0F0'), ('blue', '#00F')
        ])) == (
            ('red', 'green', 'blue'),
            ('#F00', '#0F0', '#00F'),
            (1, 1, 1)
        )
