from unittest import TestCase


class TestBeakerSessionProvider(TestCase):

    def test_get_identity(self):
        from cleaver.identity.beaker import BeakerSessionProvider

        class FakeSession(object):
            id = 'ABC123'

        environ = {'beaker.session': FakeSession()}

        provider = BeakerSessionProvider()
        assert provider.get_identity(environ) == 'ABC123'

    def test_get_identity_with_custom_environ_key(self):
        from cleaver.identity.beaker import BeakerSessionProvider

        class FakeSession(object):
            id = 'ABC123'

        environ = {'beaker.special_key': FakeSession()}

        provider = BeakerSessionProvider(environ_key='beaker.special_key')
        assert provider.get_identity(environ) == 'ABC123'
