import sys

# True if we are running on Python 3.
PY3 = sys.version_info[0] == 3
PY25 = sys.version_info[:2] == (2, 5)

try:
    next = next
except NameError:
    def next(iterator):  # noqa
        return iterator.next()

if PY3:
    from itertools import zip_longest
    from urllib.parse import urlencode, parse_qs, parse_qsl
    string_types = str
elif PY25:
    """
    http://docs.python.org/library/itertools.html#itertools.izip%5Flongest
    """
    class ZipExhausted(Exception):
        pass

    def next(iterator):
        return iterator.next()  # Fallback for Python 2.5

    def zip_longest(*args, **kwds):  # noqa
        from itertools import repeat, chain
        # zip_longest('ABCD', 'xy', fillvalue='-') --> Ax By C- D-
        fillvalue = kwds.get('fillvalue')
        counter = [len(args) - 1]

        def sentinel():
            if not counter[0]:
                raise ZipExhausted
            counter[0] -= 1
            yield fillvalue
        fillers = repeat(fillvalue)
        iterators = [chain(it, sentinel(), fillers) for it in args]
        try:
            while iterators:
                yield tuple(map(next, iterators))
        except ZipExhausted:
            pass
    from urllib import urlencode  # noqa
    from cgi import parse_qs, parse_qsl  # noqa
    string_types = basestring  # noqa
else:
    from itertools import izip_longest as zip_longest  # noqa

    from urllib import urlencode  # noqa
    from urlparse import parse_qs, parse_qsl  # noqa
    string_types = basestring  # noqa
