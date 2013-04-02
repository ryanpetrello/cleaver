from unittest import TestCase
from datetime import datetime

from mock import Mock, patch
from sqlalchemy.engine.reflection import Inspector

from cleaver import Cleaver
from cleaver.experiment import Experiment
from cleaver.tests import FakeIdentityProvider
from cleaver.backend.db import SQLAlchemyBackend, model


class TestSQLAlchemy(TestCase):

    def setUp(self):
        self.b = SQLAlchemyBackend()

    def tearDown(self):
        engine = self.b.Session.bind.connect()
        for table_name in Inspector.from_engine(engine).get_table_names():
            trans = engine.begin()

            # Attempt to truncate all data in the table and commit
            engine.execute('DELETE FROM %s' % table_name)
            trans.commit()
        engine.close()

    def test_valid_configuration(self):
        cleaver = Cleaver({}, FakeIdentityProvider(), SQLAlchemyBackend())
        assert isinstance(cleaver._identity, FakeIdentityProvider)
        assert isinstance(cleaver._backend, SQLAlchemyBackend)

    def test_save_experiment(self):
        b = self.b
        b.save_experiment('text_size', ('small', 'medium', 'large'))

        assert model.Experiment.query.count() == 1
        experiment = model.Experiment.query.first()
        assert experiment.name == 'text_size'
        assert experiment.started_on.date() == datetime.utcnow().date()

        assert len(experiment.variants) == 3
        assert experiment.variants[0].name == 'small'
        assert experiment.variants[0].experiment.name == 'text_size'
        assert experiment.variants[1].name == 'medium'
        assert experiment.variants[1].experiment.name == 'text_size'
        assert experiment.variants[2].name == 'large'
        assert experiment.variants[2].experiment.name == 'text_size'

    def test_get_experiment_no_match(self):
        b = self.b

        e = b.get_experiment('text_size', ('small', 'medium', 'large'))
        assert e is None

    def test_get_experiment(self):
        b = self.b
        b.save_experiment('text_size', ('small', 'medium', 'large'))

        e = b.get_experiment('text_size', ('small', 'medium', 'large'))
        assert isinstance(e, Experiment)

        assert e.name == 'text_size'
        assert e.started_on.date() == datetime.utcnow().date()
        assert e.variants == ('small', 'medium', 'large')

    def test_all_experiments(self):
        b = self.b
        b.save_experiment('text_size', ('small', 'medium', 'large'))
        b.save_experiment('show_promo', ('True', 'False'))

        a = b.all_experiments()
        assert len(a) == 2

        assert isinstance(a[0], Experiment)
        assert a[0].name == 'text_size'
        assert a[0].started_on.date() == datetime.utcnow().date()
        assert a[0].variants == ('small', 'medium', 'large')

        assert isinstance(a[1], Experiment)
        assert a[1].name == 'show_promo'
        assert a[1].started_on.date() == datetime.utcnow().date()
        assert a[1].variants == ('True', 'False')

    def test_is_verified_human(self):
        b = self.b
        b.Session.add(model.VerifiedHuman(identity='ryan'))
        b.Session.commit()

        assert b.is_verified_human('ryan') is True
        assert b.is_verified_human('googlebot') is False

    def test_mark_human(self):
        b = self.b

        b.mark_human('ryan')
        query = model.VerifiedHuman.query.filter_by(identity='ryan')
        assert query.count() == 1
        assert query.first() is not None

        b.mark_human('ryan')
        query = model.VerifiedHuman.query.filter_by(identity='ryan')
        assert query.count() == 1
        assert query.first() is not None

    def test_unverified_participate(self):
        b = self.b
        b.save_experiment('text_size', ('small', 'medium', 'large'))
        b.participate('ryan', 'text_size', 'medium')

        people = model.Participant.query.all()
        assert len(people) == 1

        assert people[0].identity == 'ryan'
        assert people[0].experiment.name == 'text_size'
        assert people[0].variant.name == 'medium'

        assert model.TrackedEvent.query.filter_by(
            type='PARTICIPANT'
        ).count() == 0

    @patch.object(
        SQLAlchemyBackend,
        'is_verified_human',
        Mock(return_value=True)
    )
    def test_verified_participate(self):
        b = self.b
        b.save_experiment('text_size', ('small', 'medium', 'large'))
        b.participate('ryan', 'text_size', 'medium')

        people = model.Participant.query.all()
        assert len(people) == 1

        assert people[0].identity == 'ryan'
        assert people[0].experiment.name == 'text_size'
        assert people[0].variant.name == 'medium'

        participations = model.TrackedEvent.query.filter_by(
            type='PARTICIPANT'
        ).all()
        assert len(participations) == 1

        assert participations[0].experiment.name == 'text_size'
        assert participations[0].variant.name == 'medium'
        assert participations[0].total == 1

    def test_unverified_participate_multiple(self):
        b = self.b
        b.save_experiment('text_size', ('small', 'medium', 'large'))
        b.participate('ryan', 'text_size', 'medium')
        b.participate('ryan', 'text_size', 'medium')
        b.participate('ryan', 'text_size', 'medium')

        people = model.Participant.query.all()
        assert len(people) == 1

        assert people[0].identity == 'ryan'
        assert people[0].experiment.name == 'text_size'
        assert people[0].variant.name == 'medium'

        assert model.TrackedEvent.query.filter_by(
            type='PARTICIPANT'
        ).count() == 0

    @patch.object(
        SQLAlchemyBackend,
        'is_verified_human',
        Mock(return_value=True)
    )
    def test_verified_participate_multiple(self):
        b = self.b
        b.save_experiment('text_size', ('small', 'medium', 'large'))
        b.participate('ryan', 'text_size', 'medium')
        b.participate('ryan', 'text_size', 'medium')
        b.participate('ryan', 'text_size', 'medium')

        people = model.Participant.query.all()
        assert len(people) == 1

        assert people[0].identity == 'ryan'
        assert people[0].experiment.name == 'text_size'
        assert people[0].variant.name == 'medium'

        participations = model.TrackedEvent.query.filter_by(
            type='PARTICIPANT'
        ).all()
        assert len(participations) == 1

        assert participations[0].experiment.name == 'text_size'
        assert participations[0].variant.name == 'medium'
        assert participations[0].total == 3

    def test_get_variant(self):
        b = self.b
        b.save_experiment('text_size', ('small', 'medium', 'large'))
        b.participate('ryan', 'text_size', 'medium')

        assert b.get_variant('ryan', 'text_size') == 'medium'
        assert b.get_variant('ryan', 'another_test') is None

    def test_score(self):
        b = self.b
        b.save_experiment('text_size', ('small', 'medium', 'large'))
        b.mark_conversion('text_size', 'medium')

        conversions = model.TrackedEvent.query.filter_by(
            type='CONVERSION'
        ).all()
        assert len(conversions) == 1

        assert conversions[0].experiment.name == 'text_size'
        assert conversions[0].variant.name == 'medium'
        assert conversions[0].total == 1

    def test_score_multiple(self):
        b = self.b
        b.save_experiment('text_size', ('small', 'medium', 'large'))
        b.mark_conversion('text_size', 'medium')
        b.mark_conversion('text_size', 'large')
        b.mark_conversion('text_size', 'medium')

        conversions = model.TrackedEvent.query.filter_by(
            type='CONVERSION'
        ).all()
        assert len(conversions) == 2

        for c in conversions:
            assert ((
                c.experiment.name == 'text_size' and
                c.variant.name == 'medium' and
                c.total == 2
            ) or (
                c.experiment.name == 'text_size' and
                c.variant.name == 'large' and
                c.total == 1
            ))

    def test_unverified_participants(self):
        b = self.b
        b.participate('ryan', 'text_color', 'small')
        b.participate('joe', 'text_color', 'medium')
        b.participate('joe', 'show_promo', 'True')

        assert b.participants('text_color', 'small') == 0
        assert b.participants('text_color', 'medium') == 0
        assert b.participants('text_color', 'large') == 0

        assert b.participants('show_promo', 'True') == 0
        assert b.participants('show_promo', 'False') == 0

    @patch.object(
        SQLAlchemyBackend,
        'is_verified_human',
        Mock(return_value=True)
    )
    def test_verified_participants(self):
        b = self.b
        b.save_experiment('text_size', ('small', 'medium', 'large'))
        b.save_experiment('show_promo', ('True', 'False'))
        b.participate('ryan', 'text_size', 'small')
        b.participate('joe', 'text_size', 'medium')
        b.participate('joe', 'show_promo', 'True')

        assert b.participants('text_size', 'small') == 1
        assert b.participants('text_size', 'medium') == 1
        assert b.participants('text_size', 'large') == 0

        assert b.participants('show_promo', 'True') == 1
        assert b.participants('show_promo', 'False') == 0

    def test_conversions(self):
        b = self.b
        b.save_experiment('text_size', ('small', 'medium', 'large'))
        b.save_experiment('show_promo', ('True', 'False'))
        b.mark_conversion('text_size', 'small')
        b.mark_conversion('text_size', 'medium')
        b.mark_conversion('show_promo', 'True')

        assert b.conversions('text_size', 'small') == 1
        assert b.conversions('text_size', 'medium') == 1
        assert b.conversions('text_size', 'large') == 0

        assert b.conversions('show_promo', 'True') == 1
        assert b.conversions('show_promo', 'False') == 0
