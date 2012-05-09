import sys

# True if we are running on Python 3.
PY3 = sys.version_info[0] == 3

if PY3:
    from itertools import zip_longest
    string_types = str
else:
    from itertools import izip_longest as zip_longest  # noqa
    string_types = basestring
