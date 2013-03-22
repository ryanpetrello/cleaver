import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

ModelBase = declarative_base()


class Experiment(ModelBase):
    __tablename__ = 'cleaver_experiment'

    name = sa.Column(sa.UnicodeText, primary_key=True)
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

    name = sa.Column(sa.UnicodeText, primary_key=True)
    order = sa.Column(sa.Integer)
    experiment_name = sa.Column(
        sa.UnicodeText,
        sa.ForeignKey('%s.name' % Experiment.__tablename__)
    )


class Participant(ModelBase):
    __tablename__ = 'cleaver_participant'

    identity = sa.Column(sa.UnicodeText, primary_key=True)
    experiment_name = sa.Column(
        sa.UnicodeText,
        sa.ForeignKey('%s.name' % Experiment.__tablename__),
        primary_key=True
    )
    variant = sa.Column(sa.UnicodeText)


class TrackedEvent(ModelBase):
    __tablename__ = 'cleaver_event'

    TYPES = (
        'PARTICIPANT',
        'CONVERSION'
    )

    type = sa.Column(
        sa.Enum(*TYPES, **{'native_enum': False}),
        primary_key=True
    )

    experiment_name = sa.Column(
        sa.UnicodeText,
        sa.ForeignKey('%s.name' % Experiment.__tablename__),
        primary_key=True
    )
    variant_name = sa.Column(
        sa.UnicodeText,
        sa.ForeignKey('%s.name' % Variant.__tablename__),
        primary_key=True
    )
    total = sa.Column(sa.Integer, default=0)


class VerifiedHuman(ModelBase):
    __tablename__ = 'cleaver_human'

    identity = sa.Column(sa.UnicodeText, primary_key=True)
