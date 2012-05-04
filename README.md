# Cleaver

Bloody simple A/B testing for Python WSGI applications:

* Present display or behavioral differences in one line of code.
* Measure and compare conversions amongst multiple variants, including
  statistical significance.
* Guarantee the same experience for returning users.
* Integrates easily with existing authentication and storage layers.

Cleaver is inspired by [ABingo](<http://www.bingocardcreator.com/abingo>), [Split](<https://rubygems.org/gems/split>) (Rails) and [Dabble](<https://github.com/dcrosta/dabble>) (Python).

## Starting an Experiment

Starting a new A/B test is easy.  Use this code anywhere within the context of
an HTTP request to automatically segment visitors:

    cleaver = request.environ['cleaver']
    
    # Start a new A/B experiment, returning True or False
    show_promo = cleaver.split('show_promo')
    
    # ...later, when the user completes the test, store the conversion...
    cleaver.score('show_promo')

## Specifying Alternatives

Cleaver can also be used to specify an arbitrary number of alternatives:

    cleaver = request.environ['cleaver']
    
    # Start a new A/B experiment, returning one of several options
    background_color = cleaver.split(
        'background_color',
        ('Red', '#F00'),
        ('Green', '#0F0'),
        ('Blue', '#00F')
    )

## Configuring Cleaver

Cleaver works out of the box with most WSGI frameworks.  To get started, wrap
your WSGI application with ``cleaver.SplitMiddleware``:

    from cleaver import SplitMiddleware
    from cleaver.identity.cookie import CookieIdentityProvider
    from cleaver.backend.sqlite import SQLiteBackend

    def simple_app(environ, start_response):
        # Get the session object from the environ
        cleaver = environ['cleaver']

        price = cleaver(
            'Half-Off Promotional Price',
            ('$50', '$50'),
            ('$25', '$25 (Today Only!)')
        )

        start_response('200 OK', [('Content-type', 'text/plain')])
        return ['Sign up for %s' % price]

    wsgi_app = SplitMiddleware(
        simple_app,
        CookieIdentityProvider('cookie_name'),
        SQLiteBackend(':memory:')
    )
