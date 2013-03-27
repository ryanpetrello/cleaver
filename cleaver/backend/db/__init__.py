from datetime import datetime


def _sqlalchemy_installed():
    try:
        import sqlalchemy
    except ImportError:  # pragma: nocover
        raise ImportError(
            'The database backend requires SQLAlchemy to be installed.  '
            'See http://pypi.python.org/pypi/SQLAlchemy'
        )
    return sqlalchemy
_sqlalchemy_installed()

from sqlalchemy import and_

from . import model
from .session import session_for

from cleaver.experiment import Experiment as CleaverExperiment
from cleaver.backend import CleaverBackend


class SQLAlchemyBackend(CleaverBackend):
    """
    Provides an interface for persisting and retrieving A/B test results
    to a SQLAlchemy-supported database.
    """

    def __init__(self, dburi='sqlite://', engine_options={}):
        self.dburi = dburi
        self.engine_options = engine_options
        self.Session = session_for(
            dburi=self.dburi,
            **self.engine_options
        )

    def experiment_factory(self, experiment):
        if experiment is None:
            return None
        return CleaverExperiment(
            backend=self,
            name=experiment.name,
            started_on=experiment.started_on,
            variants=tuple(v.name for v in experiment.variants)
        )

    def all_experiments(self):
        """
        Retrieve every available experiment.

        Returns a list of ``cleaver.experiment.Experiment``s
        """
        try:
            return [
                self.experiment_factory(e)
                for e in self.Session.query(model.Experiment).all()
            ]
        finally:
            self.Session.close()

    def get_experiment(self, name, variants):
        """
        Retrieve an experiment by its name and variants (assuming it exists).

        :param name a unique string name for the experiment
        :param variants a list of strings, each with a unique variant name

        Returns a ``cleaver.experiment.Experiment`` or ``None``
        """
        try:
            return self.experiment_factory(
                self.Session.query(model.Experiment).get(name)
            )
        finally:
            self.Session.close()

    def save_experiment(self, name, variants):
        """
        Persist an experiment and its variants (unless they already exist).

        :param name a unique string name for the experiment
        :param variants a list of strings, each with a unique variant name
        """
        try:
            model.Experiment(
                name=name,
                started_on=datetime.utcnow(),
                variants=[
                    model.Variant(name=v, order=i)
                    for i, v in enumerate(variants)
                ]
            )
            self.Session.commit()
        finally:
            self.Session.close()

    def is_verified_human(self, identity):
        try:
            return self.Session.query(
                model.VerifiedHuman
            ).filter_by(identity=identity).first() is not None
        finally:
            self.Session.close()

    def mark_human(self, identity):
        try:
            if self.Session.query(model.VerifiedHuman).filter_by(
                identity=identity
            ).count() == 0:
                model.VerifiedHuman(identity=identity)
                self.Session.commit()
        finally:
            self.Session.close()

    def get_variant(self, identity, experiment_name):
        """
        Retrieve the variant for a specific user and experiment (if it exists).

        :param identity a unique user identifier
        :param experiment_name the string name of the experiment

        Returns a ``String`` or `None`
        """
        try:
            match = self.Session.query(model.Participant).filter(and_(
                model.Participant.identity == identity,
                model.Participant.experiment_name == experiment_name
            )).first()
            return match.variant if match else None
        finally:
            self.Session.close()

    def set_variant(self, identity, experiment_name, variant):
        """
        Set the variant for a specific user.

        :param identity a unique user identifier
        :param experiment_name the string name of the experiment
        :param variant the string name of the variant
        """
        try:
            if self.Session.query(model.Participant).filter(and_(
                model.Participant.identity == identity,
                model.Participant.experiment_name == experiment_name,
                model.Participant.variant == variant
            )).count() == 0:
                model.Participant(
                    identity=identity,
                    experiment_name=experiment_name,
                    variant=variant
                )
                self.Session.commit()
        finally:
            self.Session.close()

    def _mark_event(self, type, experiment_name, variant):
        try:
            if self.Session.query(model.TrackedEvent).filter(and_(
                model.TrackedEvent.type == type,
                model.TrackedEvent.experiment_name == experiment_name,
                model.TrackedEvent.variant_name == variant
            )).first() is None:
                model.TrackedEvent(
                    type=type,
                    experiment_name=experiment_name,
                    variant_name=variant
                )
                self.Session.commit()
        finally:
            self.Session.close()

        try:
            self.Session.execute(
                'UPDATE %s SET total = total + 1 '
                'WHERE experiment_name = :experiment_name '
                'AND variant_name = :variant_name '
                'AND `type` = :type' % (
                    model.TrackedEvent.__tablename__
                ),
                {
                    'experiment_name': experiment_name,
                    'variant_name': variant,
                    'type': type
                }
            )
            self.Session.commit()
        finally:
            self.Session.close()

    def mark_participant(self, experiment_name, variant):
        """
        Mark a participation for a specific experiment variant.

        :param experiment_name the string name of the experiment
        :param variant the string name of the variant
        """
        self._mark_event('PARTICIPANT', experiment_name, variant)

    def mark_conversion(self, experiment_name, variant):
        """
        Mark a conversion for a specific experiment variant.

        :param experiment_name the string name of the experiment
        :param variant the string name of the variant
        """
        self._mark_event('CONVERSION', experiment_name, variant)

    def _total_events(self, type, experiment_name, variant):
        try:
            row = self.Session.query(model.TrackedEvent).filter(and_(
                model.TrackedEvent.type == type,
                model.TrackedEvent.experiment_name == experiment_name,
                model.TrackedEvent.variant_name == variant
            )).first()
            return row.total if row else 0
        finally:
            self.Session.close()

    def participants(self, experiment_name, variant):
        """
        The number of participants for a certain variant.

        Returns an integer.
        """
        return self._total_events('PARTICIPANT', experiment_name, variant)

    def conversions(self, experiment_name, variant):
        """
        The number of conversions for a certain variant.

        Returns an integer.
        """
        return self._total_events('CONVERSION', experiment_name, variant)
