import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base


class ModelBase(object):

    @classmethod
    def get_by(cls, *args, **kwargs):
        return cls.query.filter_by(*args, **kwargs).first()


ModelBase = declarative_base(cls=ModelBase)


class Experiment(ModelBase):
    __tablename__ = 'cleaver_experiment'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.Unicode(255), unique=True)
    started_on = sa.Column(sa.DateTime, index=True)

    variants = relationship(
        "Variant",
        backref="experiment",
        order_by='Variant.order'
    )
    participants = relationship(
        "Participant",
        backref="experiment"
    )
    events = relationship(
        "TrackedEvent",
        backref="experiment"
    )


class Variant(ModelBase):
    __tablename__ = 'cleaver_variant'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.Unicode(255), unique=True)
    order = sa.Column(sa.Integer)
    experiment_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('%s.id' % Experiment.__tablename__),
        index=True
    )

    events = relationship(
        "TrackedEvent",
        backref="variant"
    )

    participants = relationship(
        "Participant",
        backref="variant"
    )


class Participant(ModelBase):
    __tablename__ = 'cleaver_participant'
    __table_args__ = (UniqueConstraint('identity', 'experiment_id'),)

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    identity = sa.Column(sa.Unicode(255))
    experiment_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('%s.id' % Experiment.__tablename__)
    )
    variant_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('%s.id' % Variant.__tablename__),
        index=True
    )


class TrackedEvent(ModelBase):
    __tablename__ = 'cleaver_event'
    __table_args__ = (UniqueConstraint('type', 'experiment_id', 'variant_id'),)

    TYPES = (
        'PARTICIPANT',
        'CONVERSION'
    )

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    type = sa.Column(sa.Enum(*TYPES))

    experiment_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('%s.id' % Experiment.__tablename__),
    )
    variant_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('%s.id' % Variant.__tablename__),
    )
    total = sa.Column(sa.Integer, default=0)


class VerifiedHuman(ModelBase):
    __tablename__ = 'cleaver_human'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    identity = sa.Column(sa.Unicode(255), unique=True)
