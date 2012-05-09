from cleaver.identity import CleaverIdentityProvider
from cleaver.backend import CleaverBackend


class FakeIdentityProvider(CleaverIdentityProvider):

    def get_identity(self, environ):
        pass  # pragma: nocover


class FakeBackend(CleaverBackend):

    def all_experiments(self):
        pass  # pragma: nocover

    def get_experiment(self, name, variants):
        pass  # pragma: nocover

    def save_experiment(self, name, variants):
        pass  # pragma: nocover

    def is_verified_human(self, identity):
        return  # pragma: nocover

    def mark_human(self, identity):
        return  # pragma: nocover

    def get_variant(self, identity, experiment_name):
        pass  # pragma: nocover

    def set_variant(self, identity, experiment_name, variant):
        pass  # pragma: nocover

    def mark_participant(self, experiment_name, variant):
        pass  # pragma: nocover

    def mark_conversion(self, experiment_name, variant):
        pass  # pragma: nocover

    def participants(self, experiment_name, variant):
        pass  # pragma: nocover

    def conversions(self, experiment_name, variant):
        pass  # pragma: nocover
