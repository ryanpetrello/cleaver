from os import path

from .bottle import Bottle, view, request
from cleaver .backend import CleaverBackend

app = Bottle()
__t = lambda p: path.join(
    path.dirname(path.abspath(__file__)),
    'views',
    p
)


def format_percentage(f):
    return '{:.2%}'.format(f) if f else '-'


@app.route('/')
@view(__t('index'))
def index():
    return dict(
        backend=request.environ['cleaver.backend'],
        percentage=format_percentage
    )


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
