from collections import defaultdict

from sqlalchemy import create_engine, event
from sqlalchemy.orm import scoped_session, sessionmaker, mapper

from .model import ModelBase

_SETUP = defaultdict(lambda: False)
_ENGINES = {}
_SESSIONS = {}


def get_engine(dburi, **kwargs):
    if dburi not in _ENGINES:
        _ENGINES[dburi] = create_engine(dburi, **kwargs)
    return _ENGINES[dburi]


def session_for(dburi, **kwargs):
    engine = get_engine(dburi, **kwargs)
    if dburi not in _SESSIONS:
        _SESSIONS[dburi] = scoped_session(sessionmaker(bind=engine))
        ModelBase.query = _SESSIONS[dburi].query_property()

        # When a entity is instantiated, automatically add it to the Session
        @event.listens_for(mapper, 'init')
        def auto_add(target, args, kwargs):
            if isinstance(target, ModelBase):
                _SESSIONS[dburi].add(target)

    if not _SETUP['results']:
        ModelBase.metadata.create_all(engine)
        _SETUP['results'] = True

    return _SESSIONS[dburi]
