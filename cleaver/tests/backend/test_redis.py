from unittest import TestCase
from datetime import datetime

from mock import Mock, patch

from cleaver import Cleaver
from cleaver.experiment import Experiment
from cleaver.tests import FakeIdentityProvider
from cleaver.backend.redis import RedisBackend

import sys


def debug(msg):
    sys.stdout.write(' %s ' % str(msg))
    sys.stdout.flush()


class TestRedis(TestCase):

    def setUp(self):
        self.b = RedisBackend(prefix="testcleaver")

    def tearDown(self):
        map(self.b.redis.delete, self.b.redis.keys("testcleaver:*"))

    def test_valid_configuration(self):
        cleaver = Cleaver({}, FakeIdentityProvider(), RedisBackend())
        assert isinstance(cleaver._identity, FakeIdentityProvider)
        assert isinstance(cleaver._backend, RedisBackend)

    def test_save_experiment(self):
        b = self.b
        b.save_experiment('text_size', ('small', 'medium', 'large'))

        assert len(b.redis.keys("testcleaver:experiment:*")) == 1
        assert b.redis.zcount("testcleaver:variants:text_size", 0, 100) == 3
        experiment_key = b.redis.keys("testcleaver:experiment:*")[0]
        experiment = b.redis.hgetall(experiment_key)

        assert experiment_key.split(':')[-1] == 'text_size'
        started_on = datetime.strptime(experiment['started_on'],
                                       '%Y-%m-%dT%H:%M:%S')
        assert started_on.date() == datetime.utcnow().date()
        vkey = "testcleaver:variants:%s" % experiment_key.split(':')[-1]
        variants = tuple(b.redis.zrange(vkey, 0, 1000))

        assert len(variants) == 3
        assert variants[0] == 'small'
        assert variants[1] == 'medium'
        assert variants[2] == 'large'

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
        b.redis.sadd("testcleaver:verifiedhuman", "ryan")

        assert b.is_verified_human('ryan') is True
        assert b.is_verified_human('googlebot') is False

    def test_mark_human(self):
        b = self.b

        b.mark_human('ryan')
        query = [h for h in b.redis.smembers("testcleaver:verifiedhuman")
                 if h == "ryan"]
        assert len(query) == 1
        assert query[0] is not None

        b.mark_human('ryan')
        query = [h for h in b.redis.smembers("testcleaver:verifiedhuman")
                 if h == "ryan"]
        assert len(query) == 1
        assert query[0] is not None

    def test_unverified_participate(self):
        b = self.b
        b.save_experiment('text_size', ('small', 'medium', 'large'))
        b.participate('ryan', 'text_size', 'medium')

        people = b.redis.keys("testcleaver:participant:*")
        assert len(people) == 1
        ryan = b.redis.hgetall(people[0])

        assert people[0].split(':')[-1] == 'ryan'
        assert ryan.keys()[0] == 'text_size'
        assert ryan[ryan.keys()[0]] == 'medium'

        assert len(b.redis.keys("testcleaver:total_participations:*")) == 0

    @patch.object(
        RedisBackend,
        'is_verified_human',
        Mock(return_value=True)
    )
    def test_verified_participate(self):
        b = self.b
        b.save_experiment('text_size', ('small', 'medium', 'large'))
        b.participate('ryan', 'text_size', 'medium')

        people = b.redis.keys("testcleaver:participant:*")
        assert len(people) == 1
        ryan = b.redis.hgetall(people[0])

        assert people[0].split(':')[-1] == 'ryan'
        assert ryan.keys()[0] == 'text_size'
        assert ryan[ryan.keys()[0]] == 'medium'

        participations = b.redis.keys("testcleaver:total_participations:*")
        assert len(participations) == 1
        assert len(b.redis.zrange(participations[0], 0, 100)) == 1

        assert participations[0].split(':')[-1] == 'text_size'
        assert b.redis.zrange(participations[0], 0, 100)[0] == 'medium'
        assert len(b.redis.zrange(participations[0], 0, 100)) == 1

    def test_unverified_participate_multiple(self):
        b = self.b
        b.save_experiment('text_size', ('small', 'medium', 'large'))
        b.participate('ryan', 'text_size', 'medium')
        b.participate('ryan', 'text_size', 'medium')
        b.participate('ryan', 'text_size', 'medium')

        people = b.redis.keys("testcleaver:participant:*")
        assert len(people) == 1
        ryan = b.redis.hgetall(people[0])

        assert people[0].split(':')[-1] == 'ryan'
        assert ryan.keys()[0] == 'text_size'
        assert ryan[ryan.keys()[0]] == 'medium'

        assert len(b.redis.keys("testcleaver:total_participations:*")) == 0

    @patch.object(
        RedisBackend,
        'is_verified_human',
        Mock(return_value=True)
    )
    def test_verified_participate_multiple(self):
        b = self.b
        b.save_experiment('text_size', ('small', 'medium', 'large'))
        b.participate('ryan', 'text_size', 'medium')
        b.participate('ryan', 'text_size', 'medium')
        b.participate('ryan', 'text_size', 'medium')

        people = b.redis.keys("testcleaver:participant:*")
        assert len(people) == 1
        ryan = b.redis.hgetall(people[0])

        assert people[0].split(':')[-1] == 'ryan'
        assert ryan.keys()[0] == 'text_size'
        assert ryan[ryan.keys()[0]] == 'medium'

        participations = b.redis.keys("testcleaver:total_participations:*")
        assert len(participations) == 1

        assert participations[0].split(':')[-1] == 'text_size'
        variant = b.redis.zrange(participations[0], 0, 100)[0]
        assert variant == 'medium'
        assert int(b.redis.zscore(participations[0], variant)) == 3

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

        conversions = b.redis.keys("testcleaver:total_conversions:*")
        assert len(conversions) == 1

        assert conversions[0].split(':')[-1] == 'text_size'
        assert b.redis.zrange(conversions[0], 0, 100)[0] == 'medium'
        assert len(b.redis.zrange(conversions[0], 0, 100)) == 1

    def test_score_multiple(self):
        b = self.b
        b.save_experiment('text_size', ('small', 'medium', 'large'))
        b.mark_conversion('text_size', 'medium')
        b.mark_conversion('text_size', 'large')
        b.mark_conversion('text_size', 'medium')

        experiments_w_conv = b.redis.keys("testcleaver:total_conversions:*")
        assert len(experiments_w_conv) == 1
        key = experiments_w_conv[0]
        conversions = b.redis.zrange(key, 0, 100)
        assert len(conversions) == 2

        for c in conversions:
            assert ((
                key.split(':')[-1] == 'text_size' and
                c == 'medium' and
                int(b.redis.zscore(key, c)) == 2
            ) or (
                key.split(':')[-1] == 'text_size' and
                c == 'large' and
                int(b.redis.zscore(key, c)) == 1
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
        RedisBackend,
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
