Cleaver
=======

Bloody simple split testing for Python applications.

Cleaver is heavily inspired by the `ABingo
<http://www.bingocardcreator.com/abingo>`_, `Split
<https://rubygems.org/gems/split>`_, and `Dabble <>`_.  As such, it
easily enables developers to:

* Present display or behavioral differences in one line of code.
* Measure and compare conversions, including statistical significance.
* Guarantee behavior for return developers.
* Provide simple interfaces for user identification and persistent storage.

Starting an Experiment
----------------------

Starting a new A/B test is easy.  Use this code anywhere you'd normally write
Python to automatically segment visitors:

    from cleaver import Cleaver
    
    cleaver = Cleaver(some_session_provider, some_backend)
    
    # Start a new A/B experiment, returning True or False
    show_promo = cleaver.split('show_promo')
    
    # ...later, store a conversion...
    cleaver.score('show_promo')

Specifying Alternatives
-----------------------

Cleaver can also be used to specify an arbitrary number of alternatives:

    from cleaver import Cleaver
    
    cleaver = Cleaver(some_session_provider, some_backend)
    
    # Start a new A/B experiment, returning True or False
    background_color = cleaver.split('
        background_color',
        ('Red', '#F00'),
        ('Green', '#0F0'),
        ('Blue', '#00F')
    )
    
    # ...later, store a conversion...
    cleaver.score('background_color')

Configuring Cleaver
-------------------
Cleaver requires a ``CleaverIdentityProvider`` and ``CleaverBackend``
implementation to track users and stores results.  Luckily, a few
implementations are provided out of the box, and it's easy to write your own!
