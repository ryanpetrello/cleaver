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
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python'
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2'
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
