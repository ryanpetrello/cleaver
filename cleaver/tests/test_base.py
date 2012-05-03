from unittest import TestCase


class TestBaseConfiguration(TestCase):

    def setUp(self):
        from cleaver.backend import CleaverBackend
        from cleaver.identity import CleaverIdentityProvider

        class FakeIdentityProvider(CleaverIdentityProvider):
            def get_identity(self):
                pass  # pragma: nocover

        class FakeBackend(CleaverBackend):
            def save_test(self):
                pass  # pragma: nocover

            def get_variant(self):
                pass  # pragma: nocover

            def set_variant(self):
                pass  # pragma: nocover

            def score(self):
                pass  # pragma: nocover

        self._identity = FakeIdentityProvider
        self._backend = FakeBackend

    def test_valid_configuration(self):
        from cleaver import Cleaver
        cleaver = Cleaver(self._identity(), self._backend())
        assert isinstance(cleaver._identity, self._identity)
        assert isinstance(cleaver._backend, self._backend)

    def test_invalid_identity(self):
        from cleaver import Cleaver
        self.assertRaises(RuntimeError, Cleaver, None, self._backend())

    def test_invalid_backend(self):
        from cleaver import Cleaver
        self.assertRaises(RuntimeError, Cleaver, self._identity(), None)


class TestSplitting(TestCase):

    def setUp(self):
        import inspect
        from cleaver.backend import CleaverBackend
        from cleaver.identity import CleaverIdentityProvider

        class MemoryIdentityProvider(CleaverIdentityProvider):
            def get_identity(self):
                return 'XYZ'

        class MemoryBackend(CleaverBackend):

            tests = {}
            records = {}
            _calls = []

            def save_test(self, test_name, variants):
                self._calls.append(inspect.stack()[0][3])
                if test_name in self.tests:
                    return self.tests[test_name]
                self.tests[test_name] = variants

            def get_variant(self, identity, test_name):
                self._calls.append(inspect.stack()[0][3])
                return self.records.get((identity, test_name), {}).get('value')

            def set_variant(self, identity, test_name, variant):
                self._calls.append(inspect.stack()[0][3])
                self.records[(identity, test_name)] = {
                    'value': variant,
                    'score': 0
                }

            def score(self, identity, test_name):
                record = self.records.get((identity, test_name), {})
                record['score'] = 1

        self._identity = MemoryIdentityProvider
        self._backend = MemoryBackend

    def test_identity(self):
        from cleaver import Cleaver
        cleaver = Cleaver(self._identity(), self._backend())
        assert cleaver.identity == 'XYZ'

    def test_existing_variant_lookup(self):
        from cleaver import Cleaver
        cleaver = Cleaver(self._identity(), self._backend())

        cleaver.split('show_sidebar')
        assert cleaver._backend._calls == [
            'save_test', 'get_variant', 'set_variant'
        ]

        cleaver._backend._calls = []
        cleaver.split('show_sidebar')
        assert cleaver._backend._calls == [
            'save_test', 'get_variant'
        ]

    def test_true_false_split(self):
        from cleaver import Cleaver
        cleaver = Cleaver(self._identity(), self._backend())
        assert cleaver.split('show_sidebar') in (True, False)

        assert cleaver._backend.tests == {'show_sidebar': ['True', 'False']}
        assert cleaver._backend.records[
            ('XYZ', 'show_sidebar')
        ]['value'] in ('True', 'False')

    def test_a_b(self):
        from cleaver import Cleaver
        cleaver = Cleaver(self._identity(), self._backend())
        assert cleaver.split(
            'price', ('a', 100), ('b', 500)
        ) in (100, 500)

        assert cleaver._backend.tests == {'price': ['a', 'b']}
        assert cleaver._backend.records[
            ('XYZ', 'price')
        ]['value'] in ('a', 'b')

    def test_multivariate(self):
        from cleaver import Cleaver
        cleaver = Cleaver(self._identity(), self._backend())
        assert cleaver.split(
            'price', ('a', 100), ('b', 500), ('c', 1000)
        ) in (100, 500, 1000)

        assert cleaver._backend.tests == {'price': ['a', 'b', 'c']}
        assert cleaver._backend.records[
            ('XYZ', 'price')
        ]['value'] in ('a', 'b', 'c')

    def test_score(self):
        from cleaver import Cleaver
        cleaver = Cleaver(self._identity(), self._backend())
        cleaver.split('show_sidebar')

        assert cleaver._backend.tests == {'show_sidebar': ['True', 'False']}
        assert cleaver._backend.records[
            ('XYZ', 'show_sidebar')
        ]['value'] in ('True', 'False')
        assert cleaver._backend.records[
            ('XYZ', 'show_sidebar')
        ]['score'] == 0

        cleaver.score('show_sidebar')
        assert cleaver._backend.records[
            ('XYZ', 'show_sidebar')
        ]['score'] == 1
