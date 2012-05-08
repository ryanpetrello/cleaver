from os import path

from .bottle import Bottle, view, request
from cleaver .backend import CleaverBackend

app = Bottle()
__t = lambda p: path.join(
    path.dirname(path.abspath(__file__)),
    'views',
    p
)


def with_backend(f):
    def wrapped(*args, **kwargs):
        ns = f(*args, **kwargs)
        if isinstance(ns, dict):
            ns['backend'] = request.environ['cleaver.backend']

            def format_percentage(f):
                return '{:.2%}'.format(f) if f else '-'
            ns['percentage'] = format_percentage
        return ns
    return wrapped


@app.route('/')
@view(__t('index'))
@with_backend
def index():
    return dict()


class CleaverWebUI(object):

    def __init__(self, backend, **kw):
        """
        A WSGI app used to view statistics on Cleaver experiments.

        :param backend any implementation of
                          ``backend.CleaverBackend``
        """
        self.app = app

        if not isinstance(backend, CleaverBackend):
            raise RuntimeError(
                '%s must implement cleaver.backend.CleaverBackend' % backend
            )

        self.backend = backend

    def __call__(self, environ, start_response):
        environ['cleaver.backend'] = self.backend
        return self.app(environ, start_response)
