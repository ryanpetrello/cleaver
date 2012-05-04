from . import CleaverIdentityProvider


class BeakerSessionProvider(CleaverIdentityProvider):
    """
    An identity provider that harnesses an existing Beaker
    (http://beaker.groovie.org/) session.

    Requires that your application has been wrapped with Beaker's
    ``SessionMiddleware``.
    """

    def __init__(self, environ_key='beaker.session'):
        self.environ_key = environ_key

    def get_identity(self, environ):
        return environ[self.environ_key].id
