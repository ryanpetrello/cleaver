Cleaver
=======

Bloody simple A/B testing for Python WSGI applications:

* Present display or behavioral differences in one line of code.
* Measure and compare conversions amongst multiple variants, including
  statistical significance.
* Guarantee the same experience for returning users.
* Integrates easily with existing authentication and storage layers.

Cleaver is inspired by `ABingo
<http://www.bingocardcreator.com/abingo>`_, `Split
<https://rubygems.org/gems/split>`_ (Rails) and `Dabble
<https://github.com/dcrosta/dabble>`_ (Python).

Starting an Experiment
----------------------

Starting a new A/B test is easy.  Use this code anywhere within the context of
an HTTP request to automatically segment visitors:

    cleaver = request.environ['cleaver']
    
    # Start a new A/B experiment, returning True or False
    show_promo = cleaver.split('show_promo')
    
    # ...later, when the user completes the test, store the conversion...
    cleaver.score('show_promo')

Specifying Alternatives
-----------------------

Cleaver can also be used to specify an arbitrary number of alternatives:

    cleaver = request.environ['cleaver']
    
    # Start a new A/B experiment, returning one of several options
    background_color = cleaver.split(
        'background_color',
        ('Red', '#F00'),
        ('Green', '#0F0'),
        ('Blue', '#00F')
    )

Configuring Cleaver
-------------------
Cleaver requires a ``CleaverIdentityProvider`` and ``CleaverBackend``
implementation to track users and stores results.  Luckily, a few
implementations are provided out of the box, and it's easy to write your own!
