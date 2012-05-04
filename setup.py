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
    description="""
    """,
    long_description=None,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python'
    ],
    keywords='',
    url='',
    author='Ryan Petrello',
    author_email='ryan (at) ryanpetrello.com',
    license='MIT',
    tests_require=['mock'],
    test_suite='cleaver.tests',
    zip_safe=False,
    packages=find_packages(exclude=['ez_setup'])
)
