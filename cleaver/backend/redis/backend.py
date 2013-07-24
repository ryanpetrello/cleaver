from datetime import datetime

import redis

from cleaver.experiment import Experiment as CleaverExperiment
from cleaver.backend import CleaverBackend

__all__ = ['RedisBackend']

# hopefully 1000 is a resonable upper limit for number of experiment variants
MAX_VARIANTS = 1000

# templates for redis keys to avoid misspellings and ease future changes
REDIS_KEY_TEMPLATES = {

    # experiments are redis hashes of experiment metadata:
    #    key: {'name': experiment_name, 'started_on': isoformat_str}
    "experiment": "%(prefix)s:experiment:%(experiment_name)s",
    "all_experiments": "%(prefix)s:experiment:*",

    # variants are redis sorted sets of variant_name scored by order
    #    key: ((variant0, 0.0), (variant1, 1.0), (variant2, 2.0), ...)
    "variants": "%(prefix)s:variants:%(experiment_name)s",

    # human is a redis set of identities
    #    key: (identity8, identity5, identity0, identity1, ...)
    "human": "%(prefix)s:verifiedhuman",

    # participants are redis hashes to keep track of experiment variant
    # assignment:
    #    key: {experiment_A_name: variant_A_name,
    #          experiment_B_name: variant_B_name, ...}
    "participant": "%(prefix)s:participant:%(identity)s",

    # total_participations are redis sorted sets of variant_name scored by
    # number of participants
    #    key: ((variant2, 23.0), (variant1, 48.0), (variant0, 6.0), ...)
    "total_participations":
    "%(prefix)s:total_participations:%(experiment_name)s",

    # total_conversions are redis sorted sets of variant_name
    # scored by conversions
    #    key: ((variant1, 30.0), (variant2, 23.0), (variant0, 9.0), ...)
    "total_conversions": "%(prefix)s:total_conversions:%(experiment_name)s"
}


class RedisBackend(CleaverBackend):
    """
    Provides an interface for persisting and retrieving A/B test results
    to a redis database.
    """

    def __init__(self, prefix='cleaver', host='localhost', port=6379, db=5):
        self.prefix = prefix
        self.redis = redis.Redis(host=host, port=port, db=db)

    def _key(self, template, value=None, variant=None):
        """ convenience method for formatting REDIS_KEY_TEMPLATES """
        """
        Retrieve redis key for given query.

        Returns a redis key
        """
        assert template in REDIS_KEY_TEMPLATES
        if template == "participant":
            return REDIS_KEY_TEMPLATES[template] % {'prefix': self.prefix,
                                                    'identity': value}
        elif template in ["all_experiments", "verifiedhuman"]:
            return REDIS_KEY_TEMPLATES[template] % {'prefix': self.prefix}
        elif template in ["participations", "conversions"]:
            assert variant is not None
            return REDIS_KEY_TEMPLATES[template] % {'prefix': self.prefix,
                                                    'experiment_name': value,
                                                    'variant_name': variant}
        else:
            return REDIS_KEY_TEMPLATES[template] % {'prefix': self.prefix,
                                                    'experiment_name': value}

    def experiment_factory(self, experiment_dict):
        if experiment_dict is None:
            return None
        return CleaverExperiment(
            backend=self,
            name=experiment_dict['name'],
            started_on=experiment_dict['started_on'],
            variants=experiment_dict['variants']
        )

    def all_experiments(self):
        """
        Retrieve every available experiment.

        Returns a list of ``cleaver.experiment.Experiment``s
        """
        all_key = self._key("all_experiments")
        experiment_keys = self.redis.keys(all_key)
        experiments = []
        for key in experiment_keys:
            # get experiment data
            experiment_dict = self.redis.hgetall(key)
            # build list of Experiment objects
            if experiment_dict:
                experiments.append(
                    self.experiment_factory(
                        self._format_experiment(experiment_dict)))
        return experiments

    def _format_experiment(self, experiment_dict):
        """
        Combine an experiment's metadata and variants.

        :param experiment_dict a dict containing experiment's
        name and started_on date as a string


        Returns a dict with experiment's name, started_on as a
        datetime object and a tuple of the experiment's variants
        """
        vkey = self._key("variants", experiment_dict['name'])
        # fetch variants for given experiment
        variants = self.redis.zrange(vkey, 0, MAX_VARIANTS)
        # create datetime from stored string
        # XXX python25's strptime doesnt support `%f` directive
        # the following will probably work across the board, but it seems silly
        # to bring regular expressions into this just for python25 support
        # datetime.strptime(re.sub('\..*', '', experiment_dict['started_on']),
        # "%Y-%m-%d %H:%M:%S")
        started_on = datetime.strptime(experiment_dict['started_on'],
                                       '%Y-%m-%d %H:%M:%S.%f')
        experiment_dict.update({'variants': tuple(variants),
                                'started_on': started_on})
        return experiment_dict

    def get_experiment(self, name, variants):
        """
        Retrieve an experiment by its name and variants (assuming it exists).

        :param name a unique string name for the experiment
        :param variants a list of strings, each with a unique variant name

        Returns a ``cleaver.experiment.Experiment`` or ``None``
        """
        key = self._key("experiment", name)
        experiment_dict = self.redis.hgetall(key)
        if experiment_dict:
            return self.experiment_factory(
                self._format_experiment(experiment_dict))
        return None

    def save_experiment(self, name, variants):
        """
        Persist an experiment and its variants (unless they already exist).

        :param name a unique string name for the experiment
        :param variants a list of strings, each with a unique variant name
        """
        key = self._key("experiment", name)
        self.redis.hmset(key, {'started_on': datetime.utcnow(),
                               'name': name})
        status = []
        if (len(variants) > MAX_VARIANTS):
            raise RuntimeError('Experiments must have '
                               'fewer than 1000 variants')
        for i, v in enumerate(variants):
            vkey = self._key("variants", name)
            status.append(self.redis.zadd(vkey, v, float(i)))
        return all(status)

    def is_verified_human(self, identity):
        key = self._key("human")
        return self.redis.sismember(key, identity)

    def mark_human(self, identity):
        if not self.is_verified_human(identity):
            key = self._key("human")
            return self.redis.sadd(key, identity)

    def get_variant(self, identity, experiment_name):
        """
        Retrieve the variant for a specific user and experiment (if it exists).

        :param identity a unique user identifier
        :param experiment_name the string name of the experiment

        Returns a ``String`` or `None`
        """
        key = self._key("participant", identity)
        return self.redis.hget(key, experiment_name)

    def set_variant(self, identity, experiment_name, variant_name):
        """
        Set the variant for a specific user.

        :param identity a unique user identifier
        :param experiment_name the string name of the experiment
        :param variant_name the string name of the variant
        """
        key = self._key("participant", identity)
        if not self.redis.hexists(key, experiment_name):
            return self.redis.hmset(key, {experiment_name: variant_name})
        return False

    def mark_participant(self, experiment_name, variant_name):
        """
        Mark a participation for a specific experiment variant.

        :param experiment_name the string name of the experiment
        :param variant the string name of the variant
        """
        key = self._key("total_participations", experiment_name)
        return self.redis.zincrby(key, variant_name, 1.0)

    def mark_conversion(self, experiment_name, variant_name):
        """
        Mark a conversion for a specific experiment variant.

        :param experiment_name the string name of the experiment
        :param variant the string name of the variant
        """
        key = self._key("total_conversions", experiment_name)
        return self.redis.zincrby(key, variant_name, 1.0)

    def participants(self, experiment_name, variant_name):
        """
        The number of participants for a certain variant.

        Returns an integer.
        """
        key = self._key("total_participations", experiment_name)
        score = self.redis.zscore(key, variant_name)
        if score is not None:
            return int(score)
        return 0

    def conversions(self, experiment_name, variant_name):
        """
        The number of conversions for a certain variant.

        Returns an integer.
        """
        key = self._key("total_conversions", experiment_name)
        score = self.redis.zscore(key, variant_name)
        if score is not None:
            return int(score)
        return 0
