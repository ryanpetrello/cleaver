from unittest import TestCase


class TestBeakerSessionProvider(TestCase):

    def test_get_identity(self):
        from cleaver.identity.beaker import BeakerSessionProvider

        class FakeSession(object):
            id = 'ABC123'

        provider = BeakerSessionProvider({'beaker.session': FakeSession()})
        assert provider.get_identity() == 'ABC123'

    def test_get_identity_with_custom_environ_key(self):
        from cleaver.identity.beaker import BeakerSessionProvider

        class FakeSession(object):
            id = 'ABC123'

        provider = BeakerSessionProvider(
            {'beaker.special_key': FakeSession()},
            'beaker.special_key'
        )
        assert provider.get_identity() == 'ABC123'
