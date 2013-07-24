from unittest import TestCase
from datetime import datetime

from mock import Mock, patch

from cleaver.experiment import Experiment, VariantStat


class TestExperiment(TestCase):

    def test_control(self):
        experiment = Experiment(
            Mock(),
            'show_promo',
            datetime,
            ['True', 'False']
        )
        assert experiment.control == 'True'

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


class TestVariantStat(TestCase):

    def test_participant_count(self):
        experiment = Mock()
        experiment.participants_for.return_value = 100

        assert VariantStat('red', experiment).participant_count == 100

    def test_conversion_rate(self):
        experiment = Mock()
        experiment.participants_for.return_value = 100
        experiment.conversions_for.return_value = 10

        assert VariantStat('red', experiment).conversion_rate == 0.1

    def test_conversion_rate_with_no_participants(self):
        experiment = Mock()
        experiment.participants_for.return_value = 0
        experiment.conversions_for.return_value = 0

        assert VariantStat('red', experiment).conversion_rate == 0.0

    def test_z_score_for_control(self):
        experiment = Mock()
        experiment.control = 'red'

        v = VariantStat('red', experiment)
        assert v.z_score == 'N/A'

    def test_z_score_when_control_has_no_conversions(self):
        e = Mock()
        e.control = 'red'

        e.participants_for = lambda x: 200 if x == e.control else 500
        e.conversions_for = lambda x: 0

        v = VariantStat('green', e)
        assert v.z_score == 0

    def test_z_score(self):
        #             participating, conversions, z-score
        # Control:         182	         35         N/A
        # Variant A:       180	         45 	    1.33
        # Variant B:       189	         28 	    -1.13
        # Variant C:       188	         61 	    2.94
        # Variant D:       188	        188 	    27.648
        # Variant E:       188	        214 	    235.953
        # Variant F:       188	        215 	    Invalid
        #
        map_ = {
            'x': (182, 35),
            'a': (180, 45),
            'b': (189, 28),
            'c': (188, 61),
            'd': (188, 188),
            'e': (188, 214),
            'f': (188, 215),
        }
        e = Mock()
        e.control = 'x'

        e.participants_for = lambda x: map_[x][0]
        e.conversions_for = lambda x: map_[x][1]

        v = VariantStat('x', e)
        assert v.z_score == "N/A"

        v = VariantStat('a', e)
        assert round(v.z_score, 3) == 1.325

        v = VariantStat('b', e)
        assert round(v.z_score, 3) == -1.132

        v = VariantStat('c', e)
        assert round(v.z_score, 3) == 2.941

        v = VariantStat('d', e)
        assert round(v.z_score, 3) == 27.648

        v = VariantStat('e', e)
        assert round(v.z_score, 3) == 235.953

        v = VariantStat('f', e)
        assert v.z_score == "Invalid"

    @patch.object(VariantStat, 'z_score', 'N/A')
    def test_unknown_confidence(self):
        assert VariantStat('x', Mock()).confidence_level == "N/A"

    @patch.object(VariantStat, 'z_score', 0.0)
    def test_no_change_confidence(self):
        assert VariantStat('x', Mock()).confidence_level == "No Change"

    @patch.object(VariantStat, 'z_score', 1.649)
    def test_no_change_confidence_boundary(self):
        assert VariantStat('x', Mock()).confidence_level == "No Confidence"

    @patch.object(VariantStat, 'z_score', 1.65)
    def test_95_confidence(self):
        assert VariantStat('x', Mock()).confidence_level == "95% Confidence"

    @patch.object(VariantStat, 'z_score', 2.329)
    def test_95_confidence_boundary(self):
        assert VariantStat('x', Mock()).confidence_level == "95% Confidence"

    @patch.object(VariantStat, 'z_score', 2.33)
    def test_99_confidence(self):
        assert VariantStat('x', Mock()).confidence_level == "99% Confidence"

    @patch.object(VariantStat, 'z_score', 3.079)
    def test_99_confidence_boundary(self):
        assert VariantStat('x', Mock()).confidence_level == "99% Confidence"

    @patch.object(VariantStat, 'z_score', 3.08)
    def test_99_point_9_confidence(self):
        assert VariantStat('x', Mock()).confidence_level == "99.9% Confidence"
