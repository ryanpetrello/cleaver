# Cleaver

[ ![Image](https://secure.travis-ci.org/ryanpetrello/cleaver.png "Travis CI") ](http://travis-ci.org/#!/ryanpetrello/cleaver "Travis CI")

Bloody simple A/B testing for Python WSGI applications:

* Present display or behavioral differences in one line of code.
* Measure and compare conversions amongst multiple variants, including
  statistical significance.
* Guarantee the same experience for returning users.
* Integrates easily with existing authentication and storage layers.

Cleaver is inspired by [ABingo](<http://www.bingocardcreator.com/abingo>), [Split](<https://rubygems.org/gems/split>) (Rails) and [Dabble](<https://github.com/dcrosta/dabble>) (Python).

## Usage

### Starting an Experiment

Starting a new A/B test is *easy*.  Use this code anywhere within the context
of an HTTP request (like a controller or a template) to start automatically
segmenting visitors:

``` python
cleaver = request.environ['cleaver']

# Start a new A/B experiment, returning True or False
show_promo = cleaver('show_promo')

# ...later, when the user completes the experiment, score the conversion...
cleaver.score('show_promo')
```

### Specifying Variants

Cleaver can also be used to specify an arbitrary number of variants:

``` python
cleaver = request.environ['cleaver']

# Start a new A/B experiment, returning one of several options
background_color = cleaver(
    'background_color',
    ('Red', '#F00'),
    ('Green', '#0F0'),
    ('Blue', '#00F')
)
```

### Weighted Variants

Maybe you only want to present an experimental change to a small portion of
your user base.  Variant weights make this simple - just add a third integer
argument to each variant.
    
``` python
cleaver = request.environ['cleaver']

background_color = cleaver(
    'show_new_experimental_feature',
    ('True', True, 1),
    ('False', False, 9)
)
```

The default weight for variants, when left unspecified, is 1.

### Adding Cleaver to Your WSGI Application

Cleaver works out of the box with most WSGI frameworks.  To get started, wrap
any WSGI application with ``cleaver.SplitMiddleware``.  For example:

``` python
from cleaver import SplitMiddleware
from cleaver.backend.db import SQLAlchemyBackend

def simple_app(environ, start_response):
    # Get the session object from the environ
    cleaver = environ['cleaver']

    button_size = cleaver(
        'Button Size',
        ('Small', 12),
        ('Medium', 18),
        ('Large', 24)
    )

    start_response('200 OK', [('Content-type', 'text/html')])
    return ['<button style="font-size:%spx;">Sign Up Now!</button>' % button_size]

wsgi_app = SplitMiddleware(
    simple_app,
    lambda environ: environ['REMOTE_ADDR'],  # Track by IP for examples' sake
    SQLAlchemyBackend('sqlite:///experiment.data')
)
```

``cleaver.SplitMiddleware`` requires an identity and backend adaptor (for
recognizing returning visitors and storing statistical data).  Luckily, Cleaver
comes with a few out of the box, such as support for [Beaker
sessions](http://beaker.groovie.org/), and storage via
[SQLAlchemy](http://www.sqlalchemy.org/) or [Redis](http://redis.io/).
Implementing your own is easy too;
just have a look at the full documentation <link>.

### Overriding Variants
For QA and testing purposes, you may need to force your application to always
return a certain variant.

``` python
    wsgi_app = SplitMiddleware(
        simple_app,
        ...
        allow_override=True
    )
```

If your application has an experiment called ``button_size`` with variants
called `small`, `medium`, and `large`, a url in the format:

    http://mypythonapp.com?cleaver:button_size=small

..will always display small buttons. This data won't, however, count towards
reporting.

### Blocking Robots

By default, Cleaver does not differentiate between robots (such as
[Googlebot](http://en.wikipedia.org/wiki/Googlebot)) and living, breathing,
browser-driving humans.

This can cause participants well in excess of the number of actual humans who
come to your site (if your A/B tests are publicly visible), and since bots
don't generally convert, can result in skewed conversion metrics.

To combat this, Cleaver can be configured to defer counting of visitors as
participants until after they've proven they're probably not a bot:

``` python
    wsgi_app = SplitMiddleware(
        simple_app,
        ...
        count_humans_only=True
    )
```

...and then, on every page that presents an A/B decision, add the following
call directly prior to the closing ``</body>`` tag (adapted to your templating
language of choice):

    ...
            {{request.environ['cleaver'].humanizing_javascript()}}
        </body>
    </html>

## Analyzing Results

Cleaver comes with a lightweight WSGI front end which can be used to see how
your experiments are going.

``` python
    from cleaver.reports.web import CleaverWebUI
    from cleaver.backend.db import SQLAlchemyBackend
    
    wsgi_app = CleaverWebUI(
        SQLAlchemyBackend('sqlite:///experiment.data')
    )
    
    from wsgiref import simple_server
    simple_server.make_server('', 8000, wsgi_app).serve_forever()
```

<img src="http://imgur.com/y1SUf.png" />

## Development

Source hosted at [GitHub](https://github.com/ryanpetrello/cleaver). Report
issues and feature requests on [GitHub
Issues](https://github.com/ryanpetrello/cleaver/issues).

Tests can be run with ``python setup.py test`` or ``tox``.

All contributions must:

* Include accompanying tests.
* Include narrative and API documentation if new features are added.
* Be (generally) compliant with PEP8.
* Not break the tests or build. Before issuing a pull request, ``$ pip
  install tox && tox`` from your source to ensure that all tests still pass
  across multiple versions of Python.
* Add your name to the (bottom of the) AUTHORS file.
