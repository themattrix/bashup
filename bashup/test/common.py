import sys
from contextlib import contextmanager
from difflib import unified_diff
from pprint import pformat

try:
    # pylint: disable=wrong-import-order
    from cStringIO import StringIO
except ImportError:          # pragma: no cover
    # pylint: disable=wrong-import-order
    from io import StringIO  # pragma: no cover

try:
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    # pylint: disable=invalid-name
    basestring
except NameError:     # pragma: no cover
    # pylint: disable=invalid-name,redefined-builtin
    basestring = str  # pragma: no cover


def diff(actual, expected):
    p_actual = (
        actual if isinstance(actual, basestring) else
        pformat(actual))     # pragma: no cover

    p_expect = (
        expected if isinstance(expected, basestring) else
        pformat(expected))   # pragma: no cover

    return '\n'.join(unified_diff(
        p_actual.splitlines(),
        p_expect.splitlines(),
        fromfile='actual',
        tofile='expected'))  # pragma: no cover


def assert_eq(actual, expected):
    try:
        assert actual == expected
    except AssertionError:                  # pragma: no cover
        raise AssertionError(
            '\n' + diff(actual, expected))  # pragma: no cover


@contextmanager
def captured_stdout():
    old_out = sys.stdout
    try:
        sys.stdout = StringIO()
        yield sys.stdout
    finally:
        sys.stdout = old_out
