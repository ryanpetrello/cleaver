from .compat import zip_longest, string_types, next
from .backend import CleaverBackend
from .identity import CleaverIdentityProvider
from cleaver import util


class Cleaver(object):

    def __init__(self, environ, identity, backend,
                 count_humans_only=False,
                 human_callback_token='__cleaver_human_verification__'):
        """
        Create a new Cleaver instance.

        Not generally instantiated directly, but established automatically by
        ``cleaver.SplitMiddleware`` and used within a WSGI application via
        ``request.environ['cleaver']``.

        :param environ the WSGI environ dictionary for the current request
        :param identity any implementation of
                          ``identity.CleaverIdentityProvider`` or
                          a callable that emulates
                          ``identity.CleaverIdentityProvider.get_identity``.
        :param backend any implementation of
                          ``backend.CleaverBackend``
        :param count_humans_only when False, every request (including those
                                 originating from bots and web crawlers) is
                                 treated as a unique visit (defaults to False).
        :param human_callback_token when ``count_humans_only`` is True, this
                                    token in the URL will trigger a simple
                                    verification process for humans.
        """

        if not isinstance(identity, CleaverIdentityProvider) and \
                not callable(identity):
            raise RuntimeError(
                '%s must be callable or implement '
                'cleaver.identity.CleaverIdentityProvider' % identity
            )
        if not isinstance(backend, CleaverBackend):
            raise RuntimeError(
                '%s must implement cleaver.backend.CleaverBackend' % backend
            )
        self._identity = identity
        self._backend = backend
        self._environ = environ
        self.count_humans_only = count_humans_only
        self.human_callback_token = human_callback_token

    def __call__(self, *args):
        return self.split(*args)

    @property
    def identity(self):
        """
        A unique identifier for the current visitor.
        """
        if hasattr(self._identity, 'get_identity'):
            return self._identity.get_identity(self._environ)
        return self._identity(self._environ)

    @property
    def human(self):
        return self._backend.is_verified_human(self.identity)

    def split(self, experiment_name, *variants):
        """
        Used to split and track user experience amongst one or more variants.

        :param experiment_name a unique string name for the experiment
        :param *variants can take many forms, depending on usage.

            Variants should be provided as arbitrary tuples in the
            format ('unique_string_label', any_value), ... e.g.,

            >>> split('text_color', ('red', '#F00'), ('blue', '#00F'))

            ...where the first variant (in this example, 'red') represents the
            control and any additional variants represent alternatives.

            By default, variants are chosen with equal weight.  You can tip the
            scales if you like by passing a proportional *integer* weight as
            the third element in each variant tuple:

            >>> split('text_color', ('red', '#F00', 2), ('blue', '#00F', 4))

            Optionally, variants may be excluded entirely to fall back to
            a simple True/False 50/50 split, where True is the control and
            False is the experiment, e.g.,

            >>> sidebar() if split('include_sidebar') else empty()

        """
        # Perform some minimal type checking
        if not isinstance(experiment_name, string_types):
            raise RuntimeError(
                'Invalid experiment name: %s must be a string.' %
                experiment_name
            )

        keys, values, weights = self._parse_variants(variants)
        b = self._backend

        # Record the experiment if it doesn't exist already
        experiment = b.get_experiment(experiment_name, keys)

        # If the current visitor hasn't been verified as a human, and we've not
        # required human verification, go ahead and mark them as a human.
        if self.count_humans_only is False and self.human is not True:
            b.mark_human(self.identity)

        if experiment is None:
            b.save_experiment(experiment_name, keys)
            experiment = b.get_experiment(experiment_name, keys)
        else:
            if set(experiment.variants) != set(keys):
                raise RuntimeError(
                    'An experiment named %s already exists with different '
                    'variants.' % experiment_name
                )

        # Retrieve the variant assigned to the current user
        if experiment.name in self._environ.get('cleaver.override', {}):
            variant = self._environ['cleaver.override'][experiment.name]
        else:
            variant = b.get_variant(self.identity, experiment.name)
            if variant is None:
                # ...or choose (and store) one randomly if it doesn't exist yet
                variant = next(util.random_variant(keys, weights))
                b.participate(self.identity, experiment.name, variant)

        return dict(zip(keys, values))[variant]

    def score(self, experiment_name):
        """
        Used to mark the current user's experiment variant as "converted" e.g.,

        "Suzy, who was shown the large button, just signed up."

        Conversions will *only* be marked for visitors who have been verified
        as humans (to avoid skewing reports with requests from bots and web
        crawlers).

        :param experiment_name the string name of the experiment
        """
        if self._backend.get_variant(self.identity, experiment_name) and \
                self.human is True:
            self._backend.mark_conversion(
                experiment_name,
                self._backend.get_variant(self.identity, experiment_name)
            )

    def _parse_variants(self, variants):
        if not len(variants):
            variants = [('True', True), ('False', False)]

        if len(variants) == 1:
            raise RuntimeError(
                'Experiments must have at least two variants '
                '(a control and an alternative).'
            )

        def add_defaults(v):
            if len(v) < 3:
                v = tuple(
                    list(v) + (
                        [None, 1] if len(v) == 1 else [1]
                    )
                )

            # Perform some minimal type checking
            if not isinstance(v[0], string_types):
                raise RuntimeError(
                    'Invalid variant name: %s must be a string.' %
                    v[0]
                )
            if not isinstance(v[2], int):
                raise RuntimeError(
                    'Invalid variant weight: %s must be an integer.' %
                    v[2]
                )

            return v

        variants = map(
            add_defaults,
            variants
        )

        return zip_longest(*variants)

    def humanizing_javascript(self):
        if self.human:
            return ''
        return """
            <script type="text/javascript">
               var x = Math.floor(Math.random()*100);
               var y = Math.floor(Math.random()*100);

               var url = "%s";
               var params = "x="+x+"&y="+y+"&z="+(x+y);

               var h;
               if (window.XMLHttpRequest){
                   h = new XMLHttpRequest();
               } else {
                   h = new ActiveXObject("Microsoft.XMLHTTP");
               }
               h.open("POST", url, true);
               h.setRequestHeader("Content-Type", "%s");
               h.setRequestHeader("Connection", "close");
               h.send(params);
            </script>
        """ % (self.human_callback_token, "application/x-www-form-urlencoded")
