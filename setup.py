# -*- coding: utf-8 -*-
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages  # noqa

from cleaver import __version__

setup(
    name='cleaver',
    version=__version__,
    description="""Bloody simple A/B testing for Python WSGI applications""",
    long_description="",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware'
    ],
    keywords='ab a/b split testing wsgi multivariate conversion',
    url='http://github.com/ryanpetrello/cleaver',
    author='Ryan Petrello',
    author_email='ryan (at) ryanpetrello.com',
    license='MIT',
    tests_require=['mock', 'sqlalchemy'],
    test_suite='cleaver.tests',
    zip_safe=False,
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True
)
