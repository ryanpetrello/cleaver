import sys

# True if we are running on Python 3.
PY3 = sys.version_info[0] == 3

if PY3:
    from itertools import zip_longest
    from urllib.parse import urlencode, parse_qsl
    string_types = str
else:
    from itertools import izip_longest as zip_longest  # noqa
    from urllib import urlencode  # noqa
    from urlparse import parse_qsl  # noqa
    string_types = basestring
