from unittest import TestCase
from datetime import datetime

from cleaver import Cleaver
from cleaver.experiment import Experiment
from cleaver.tests import FakeIdentityProvider
from cleaver.backend.sqlite import SQLiteBackend


class TestSQLite(TestCase):

    def setUp(self):
        self.b = SQLiteBackend()

    def tearDown(self):
        self.b.close()

    def test_valid_configuration(self):
        cleaver = Cleaver({}, FakeIdentityProvider(), SQLiteBackend())
        assert isinstance(cleaver._identity, FakeIdentityProvider)
        assert isinstance(cleaver._backend, SQLiteBackend)

    def test_save_experiment(self):
        b = self.b
        b.save_experiment('text_size', ('small', 'medium', 'large'))

        rows = b.execute(
            'SELECT name, started_on as "started_on [timestamp]" FROM e'
        ).fetchall()
        assert len(rows) == 1
        assert rows[0]['name'] == 'text_size'
        assert rows[0]['started_on'].date() == datetime.utcnow().date()

        rows = b.execute(
            'SELECT name, experiment_name FROM v'
        ).fetchall()
        assert len(rows) == 3
        assert rows[0]['name'] == 'small'
        assert rows[0]['experiment_name'] == 'text_size'
        assert rows[1]['name'] == 'medium'
        assert rows[1]['experiment_name'] == 'text_size'
        assert rows[2]['name'] == 'large'
        assert rows[2]['experiment_name'] == 'text_size'

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

    def test_participate(self):
        b = self.b
        b.save_experiment('text_size', ('small', 'medium', 'large'))
        b.participate('ryan', 'text_size', 'medium')

        people = b.execute('SELECT * FROM i').fetchall()
        assert len(people) == 1

        assert people[0]['identity'] == 'ryan'
        assert people[0]['experiment_name'] == 'text_size'
        assert people[0]['variant'] == 'medium'

        participations = b.execute("SELECT * FROM p").fetchall()
        assert len(participations) == 1

        assert participations[0]['experiment_name'] == 'text_size'
        assert participations[0]['variant'] == 'medium'
        assert participations[0]['total'] == 1

    def test_participate_multiple(self):
        b = self.b
        b.save_experiment('text_size', ('small', 'medium', 'large'))
        b.participate('ryan', 'text_size', 'medium')
        b.participate('ryan', 'text_size', 'medium')
        b.participate('ryan', 'text_size', 'medium')

        people = b.execute('SELECT * FROM i').fetchall()
        assert len(people) == 1

        assert people[0]['identity'] == 'ryan'
        assert people[0]['experiment_name'] == 'text_size'
        assert people[0]['variant'] == 'medium'

        participations = b.execute("SELECT * FROM p").fetchall()
        assert len(participations) == 1

        assert participations[0]['experiment_name'] == 'text_size'
        assert participations[0]['variant'] == 'medium'
        assert participations[0]['total'] == 3

    def test_get_variant(self):
        b = self.b
        b.save_experiment('text_size', ('small', 'medium', 'large'))
        b.participate('ryan', 'text_size', 'medium')

        assert b.get_variant('ryan', 'text_size') == 'medium'
        assert b.get_variant('ryan', 'another_test') == None

    def test_score(self):
        b = self.b
        b.score('text_size', 'medium')

        conversions = b.execute('SELECT * FROM c').fetchall()
        assert len(conversions) == 1

        assert conversions[0]['experiment_name'] == 'text_size'
        assert conversions[0]['variant'] == 'medium'
        assert conversions[0]['total'] == 1

    def test_score_multiple(self):
        b = self.b
        b.score('text_size', 'medium')
        b.score('text_size', 'large')
        b.score('text_size', 'medium')

        conversions = b.execute('SELECT * FROM c').fetchall()
        assert len(conversions) == 2

        assert conversions[0]['experiment_name'] == 'text_size'
        assert conversions[0]['variant'] == 'medium'
        assert conversions[0]['total'] == 2

        assert conversions[1]['experiment_name'] == 'text_size'
        assert conversions[1]['variant'] == 'large'
        assert conversions[1]['total'] == 1

    def test_participants(self):
        b = self.b
        b.participate('ryan', 'text_color', 'small')
        b.participate('joe', 'text_color', 'medium')
        b.participate('joe', 'show_promo', 'True')

        assert b.participants('text_color', 'small') == 1
        assert b.participants('text_color', 'medium') == 1
        assert b.participants('text_color', 'large') == 0

        assert b.participants('show_promo', 'True') == 1
        assert b.participants('show_promo', 'False') == 0

    def test_conversions(self):
        b = self.b
        b.score('text_color', 'small')
        b.score('text_color', 'medium')
        b.score('show_promo', 'True')

        assert b.conversions('text_color', 'small') == 1
        assert b.conversions('text_color', 'medium') == 1
        assert b.conversions('text_color', 'large') == 0

        assert b.conversions('show_promo', 'True') == 1
        assert b.conversions('show_promo', 'False') == 0
