from unittest import TestCase
from datetime import datetime

from mock import patch

from . import FakeIdentityProvider, FakeBackend
from cleaver import Cleaver
from cleaver.experiment import Experiment


class TestBase(TestCase):

    def test_valid_configuration(self):
        cleaver = Cleaver({}, FakeIdentityProvider(), FakeBackend())
        assert isinstance(cleaver._identity, FakeIdentityProvider)
        assert isinstance(cleaver._backend, FakeBackend)

    def test_invalid_identity(self):
        self.assertRaises(
            RuntimeError,
            Cleaver,
            {},
            None,
            FakeIdentityProvider()
        )

    def test_invalid_backend(self):
        self.assertRaises(
            RuntimeError,
            Cleaver,
            {},
            FakeIdentityProvider(),
            None
        )

    @patch.object(FakeIdentityProvider, 'get_identity')
    def test_identity(self, get_identity):
        cleaver = Cleaver({}, FakeIdentityProvider(), FakeBackend())
        get_identity.return_value = 'ABC123'

        assert cleaver.identity == 'ABC123'

    def test_callable_identity(self):
        cleaver = Cleaver({}, lambda environ: 'ABC456', FakeBackend())
        assert cleaver.identity == 'ABC456'


class TestSplit(TestCase):

    def test_experiment_name_must_be_a_string(self):
        cleaver = Cleaver({}, FakeIdentityProvider(), FakeBackend())
        self.assertRaises(
            RuntimeError,
            cleaver.split,
            500
        )

    @patch.object(FakeBackend, 'get_experiment')
    @patch.object(FakeBackend, 'save_experiment')
    def test_experiment_save(self, save_experiment, get_experiment):
        backend = FakeBackend()
        get_experiment.side_effect = [
            None,  # the first call fails
            Experiment(
                backend=backend,
                name='show_promo',
                started_on=datetime.utcnow(),
                variants=['True', 'False']
            )  # but the second call succeeds after a successful save
        ]
        cleaver = Cleaver({}, FakeIdentityProvider(), backend)

        assert cleaver.split('show_promo') in (True, False)
        get_experiment.assert_called_with('show_promo', ('True', 'False'))
        save_experiment.assert_called_with('show_promo', ('True', 'False'))

    @patch.object(FakeBackend, 'get_experiment')
    @patch.object(FakeBackend, 'save_experiment')
    def test_experiment_save_conflict(self, save_experiment, get_experiment):
        """
        If an experiment is saved with a certain name and variants, and then
        is created later with a different set of variants, e.g.,

        split('show_promo', ('True', True), ('False', False))
        split('show_promo', ('T', True), ('F', False))

        ...an exception should be thrown.
        """
        backend = FakeBackend()
        created = Experiment(
            backend=backend,
            name='show_promo',
            started_on=datetime.utcnow(),
            variants=['True', 'False']
        )
        get_experiment.side_effect = [
            None,  # the first call fails
            created,  # but the second call succeeds after a successful save
            created
        ]
        cleaver = Cleaver({}, FakeIdentityProvider(), backend)

        assert cleaver.split('show_promo') in (True, False)
        get_experiment.assert_called_with('show_promo', ('True', 'False'))
        save_experiment.assert_called_with('show_promo', ('True', 'False'))

        self.assertRaises(
            RuntimeError,
            cleaver.split,
            'show_promo',
            ('T', True),
            ('F', False)
        )

    @patch.object(FakeBackend, 'get_experiment')
    def test_experiment_get(self, get_experiment):
        backend = FakeBackend()
        get_experiment.return_value = Experiment(
            backend=backend,
            name='show_promo',
            started_on=datetime.utcnow(),
            variants=['True', 'False']
        )
        cleaver = Cleaver({}, FakeIdentityProvider(), backend)

        assert cleaver.split('show_promo') in (True, False)
        get_experiment.assert_called_with('show_promo', ('True', 'False'))

    @patch.object(FakeBackend, 'get_experiment')
    @patch.object(FakeBackend, 'mark_human')
    @patch.object(Cleaver, 'identity', 'ABC123')
    @patch.object(Cleaver, 'human', False)
    def test_default_human_verification(self, mark_human, get_experiment):
        backend = FakeBackend()
        get_experiment.return_value = Experiment(
            backend=backend,
            name='show_promo',
            started_on=datetime.utcnow(),
            variants=['True', 'False']
        )
        cleaver = Cleaver({}, FakeIdentityProvider(), backend)

        assert cleaver.split('show_promo') in (True, False)
        mark_human.assert_called_with('ABC123')

    @patch('cleaver.util.random_variant')
    @patch.object(FakeBackend, 'get_experiment')
    @patch.object(FakeBackend, 'participate')
    @patch.object(FakeIdentityProvider, 'get_identity')
    def test_variant_participation(self, get_identity, participate,
                                   get_experiment, random_variant):
        cleaver = Cleaver({}, FakeIdentityProvider(), FakeBackend())
        get_experiment.return_value.name = 'show_promo'
        get_experiment.return_value.variants = ('True', 'False')
        get_identity.return_value = 'ABC123'
        random_variant.return_value = iter(['True'])

        assert cleaver.split('show_promo') in (True, False)
        participate.assert_called_with('ABC123', 'show_promo', 'True')

    @patch.object(FakeBackend, 'get_experiment')
    def test_variant_override(self, get_experiment):
        cleaver = Cleaver({
            'cleaver.override': {'show_promo': 'False'}
        }, FakeIdentityProvider(), FakeBackend())
        get_experiment.return_value.name = 'show_promo'
        get_experiment.return_value.variants = ('True', 'False')

        assert cleaver.split('show_promo') is False

    @patch.object(FakeBackend, 'mark_conversion')
    @patch.object(FakeBackend, 'get_variant')
    @patch.object(FakeBackend, 'is_verified_human', lambda *args: True)
    @patch.object(FakeIdentityProvider, 'get_identity')
    def test_score(self, get_identity, get_variant, mark_conversion):
        cleaver = Cleaver({}, FakeIdentityProvider(), FakeBackend())
        get_variant.return_value = 'red'
        get_identity.return_value = 'ABC123'

        cleaver.score('primary_color')
        mark_conversion.assert_called_with('primary_color', 'red')


class TestVariants(TestCase):

    def test_minimum_two_arguments(self):
        c = Cleaver({}, FakeIdentityProvider(), FakeBackend())
        self.assertRaises(
            RuntimeError,
            c._parse_variants,
            (('red', '#F00'),)
        )

    def test_true_false(self):
        c = Cleaver({}, FakeIdentityProvider(), FakeBackend())
        assert tuple(c._parse_variants(())) == (
            ('True', 'False'),
            (True, False),
            (1, 1)
        )

    def test_a_b(self):
        c = Cleaver({}, FakeIdentityProvider(), FakeBackend())
        assert tuple(c._parse_variants((
            ('red', '#F00'), ('green', '#0F0')
        ))) == (
            ('red', 'green'),
            ('#F00', '#0F0'),
            (1, 1)
        )

    def test_multivariate(self):
        c = Cleaver({}, FakeIdentityProvider(), FakeBackend())
        assert tuple(c._parse_variants((
            ('red', '#F00'), ('green', '#0F0'), ('blue', '#00F')
        ))) == (
            ('red', 'green', 'blue'),
            ('#F00', '#0F0', '#00F'),
            (1, 1, 1)
        )

    def test_weighted_variants(self):
        c = Cleaver({}, FakeIdentityProvider(), FakeBackend())
        assert tuple(c._parse_variants((
            ('red', '#F00', 1), ('green', '#0F0', 2), ('blue', '#00F', 5)
        ))) == (
            ('red', 'green', 'blue'),
            ('#F00', '#0F0', '#00F'),
            (1, 2, 5)
        )

    def test_variants_must_be_strings(self):
        c = Cleaver({}, FakeIdentityProvider(), FakeBackend())
        self.assertRaises(
            RuntimeError,
            c._parse_variants,
            ((5, 'five'), (8, 'eight'))
        )

    def test_variants_with_empty_value(self):
        """
        Variants where the value is None should be acceptable.
        """
        c = Cleaver({}, FakeIdentityProvider(), FakeBackend())
        assert tuple(c._parse_variants((('five', 5), ('nothing', None)))) == (
            ('five', 'nothing'),
            (5, None),
            (1, 1)
        )

    def test_variants_with_missing_values(self):
        """
        Variants with missing values should default to None
        """
        c = Cleaver({}, FakeIdentityProvider(), FakeBackend())
        assert tuple(c._parse_variants((('five', 5, 2), ('nothing',)))) == (
            ('five', 'nothing'),
            (5, None),
            (2, 1)
        )

    def test_variants_with_missing_weights(self):
        """
        Variants with missing weights should default to 1
        """
        c = Cleaver({}, FakeIdentityProvider(), FakeBackend())
        assert tuple(c._parse_variants((('five', 5, 10), ('two', 2)))) == (
            ('five', 'two'),
            (5, 2),
            (10, 1)
        )

    def test_variant_weights_must_be_integers(self):
        c = Cleaver({}, FakeIdentityProvider(), FakeBackend())
        self.assertRaises(
            RuntimeError,
            c._parse_variants,
            (('red', '#F00', .5), ('green', '#0F0', 2.5))
        )


class TestHumanizingJavascript(TestCase):

    def test_url_check(self):
        c = Cleaver({}, FakeIdentityProvider(), FakeBackend())
        assert 'var url = "%s";' % c.human_callback_token in \
            c.humanizing_javascript()

    @patch.object(Cleaver, 'human', True)
    def test_already_human(self):
        c = Cleaver({}, FakeIdentityProvider(), FakeBackend())
        assert c.humanizing_javascript() == ''
