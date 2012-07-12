from datetime import datetime
import sqlite3

from cleaver.experiment import Experiment
from cleaver.backend import CleaverBackend


class SQLiteBackend(CleaverBackend):
    """
    Provides an interface for persisting and retrieving A/B test results
    to a SQLite database.

    Primarily a proof of concept/example implementation.
    """

    def __init__(self, db=':memory:'):
        self._conn = sqlite3.connect(
            db,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        self._conn.row_factory = sqlite3.Row

        # list of experiments
        self.execute(
            "CREATE TABLE IF NOT EXISTS e "
            "(name TEXT PRIMARY KEY, started_on TEXT)"
        )

        # collection of variants for an experiment
        self.execute(
            "CREATE TABLE IF NOT EXISTS v "
            "(name TEXT PRIMARY KEY, experiment_name TEXT, _ord INTEGER)"
        )

        # mapping between (identity, experiment_name) and variant
        self.execute(
            "CREATE TABLE IF NOT EXISTS i ("
            "identity TEXT PRIMAY KEY,"
            "experiment_name TEXT,"
            "variant TEXT,"
            "PRIMARY KEY (identity, experiment_name)"
            ")"
        )

        # counters for participants
        self.execute(
            "CREATE TABLE IF NOT EXISTS p ("
            "experiment_name TEXT,"
            "variant TEXT,"
            "total INTEGER DEFAULT 0,"
            "PRIMARY KEY (experiment_name, variant)"
            ")"
        )

        # counters for conversions
        self.execute(
            "CREATE TABLE IF NOT EXISTS c ("
            "experiment_name TEXT,"
            "variant TEXT,"
            "total INTEGER DEFAULT 0,"
            "PRIMARY KEY (experiment_name, variant)"
            ")"
        )

        # verified humans
        self.execute(
            "CREATE TABLE IF NOT EXISTS h ("
            "identity TEXT,"
            "PRIMARY KEY (identity)"
            ")"
        )

    def execute(self, sql, params=()):
        c = self._conn.cursor()
        try:
            r = c.execute(sql, params)
            self._conn.commit()
            return r
        except:  # pragma: nocover
            self._conn.rollback()
            raise

    def close(self):
        self._conn.close()

    def experiment_factory(self, row):
        return Experiment(
            backend=self,
            name=row['name'],
            started_on=row['started_on'],
            variants=tuple(
                v['name']
                for v in self.execute(
                    "SELECT * FROM v WHERE experiment_name = ? ORDER BY _ord",
                    (row['name'],)
                )
            )
        )

    def all_experiments(self):
        """
        Retrieve every available experiment.

        Returns a list of ``cleaver.experiment.Experiment``s
        """
        experiments = []
        for row in self.execute(
            'SELECT name, started_on as "started_on [timestamp]" FROM e'
        ):
            experiments.append(self.experiment_factory(row))
        return experiments

    def get_experiment(self, name, variants):
        """
        Retrieve an experiment by its name and variants (assuming it exists).

        :param name a unique string name for the experiment
        :param variants a list of strings, each with a unique variant name

        Returns a ``cleaver.experiment.Experiment`` or ``None``
        """
        row = self.execute(
            'SELECT name, started_on as "started_on [timestamp]" FROM e '
            'WHERE name=?',
            (name,)
        ).fetchone()
        return self.experiment_factory(row) if row else None

    def save_experiment(self, name, variants):
        """
        Persist an experiment and its variants (unless they already exist).

        :param name a unique string name for the experiment
        :param variants a list of strings, each with a unique variant name
        """
        self.execute('INSERT INTO e (name, started_on) VALUES (?, ?)', (
            name,
            datetime.utcnow()
        ))
        for i, v in enumerate(variants):
            self.execute(
                'INSERT INTO v (name, experiment_name, _ord) VALUES (?, ?, ?)',
                (v, name, i)
            )

    def is_verified_human(self, identity):
        return self.execute(
            'SELECT identity FROM h WHERE identity=?',
            (identity,)
        ).fetchone() is not None

    def mark_human(self, identity):
        self.execute(
            'INSERT OR IGNORE INTO h (identity) VALUES (?)',
            (identity,)
        )

    def get_variant(self, identity, experiment_name):
        """
        Retrieve the variant for a specific user and experiment (if it exists).

        :param identity a unique user identifier
        :param experiment_name the string name of the experiment

        Returns a ``String`` or `None`
        """
        row = self.execute(
            'SELECT * FROM i WHERE identity = ? AND experiment_name = ?',
            (identity, experiment_name)
        ).fetchone()
        return row['variant'] if row else None

    def set_variant(self, identity, experiment_name, variant):
        """
        Set the variant for a specific user.

        :param identity a unique user identifier
        :param experiment_name the string name of the experiment
        :param variant the string name of the variant
        """
        self.execute(
            'INSERT OR IGNORE INTO i (identity, experiment_name, variant) '
            'VALUES (?, ?, ?)',
            (identity, experiment_name, variant)
        )

    def mark_participant(self, experiment_name, variant):
        """
        Mark a participation for a specific experiment variant.

        :param experiment_name the string name of the experiment
        :param variant the string name of the variant
        """
        self.execute(
            'INSERT OR IGNORE INTO p (experiment_name, variant) VALUES (?, ?)',
            (experiment_name, variant)
        )
        self.execute(
            'UPDATE p SET total = total + 1 WHERE '
            'experiment_name = ? AND variant = ?',
            (experiment_name, variant)
        )

    def mark_conversion(self, experiment_name, variant):
        """
        Mark a conversion for a specific experiment variant.

        :param experiment_name the string name of the experiment
        :param variant the string name of the variant
        """
        self.execute(
            'INSERT OR IGNORE INTO c (experiment_name, variant) VALUES (?, ?)',
            (experiment_name, variant)
        )
        self.execute(
            'UPDATE c SET total = total + 1 WHERE '
            'experiment_name = ? AND variant = ?',
            (experiment_name, variant)
        )

    def participants(self, experiment_name, variant):
        """
        The number of participants for a certain variant.

        Returns an integer.
        """
        row = self.execute(
            'SELECT total FROM p WHERE experiment_name = ? AND variant = ?',
            (experiment_name, variant)
        ).fetchone()
        return int(row['total']) if row and row['total'] else 0

    def conversions(self, experiment_name, variant):
        """
        The number of conversions for a certain variant.

        Returns an integer.
        """
        row = self.execute(
            'SELECT total FROM c WHERE experiment_name = ? AND variant = ?',
            (experiment_name, variant)
        ).fetchone()
        return int(row['total']) if row and row['total'] else 0
