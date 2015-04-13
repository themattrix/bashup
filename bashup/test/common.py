from difflib import unified_diff
from pprint import pformat


try:
    basestring        # pylint: disable=invalid-name
except NameError:     # pragma: no cover
    basestring = str  # pragma: no cover  pylint: disable=invalid-name


def diff(actual, expected):
    pactual = (
        actual if isinstance(actual, basestring) else
        pformat(actual))     # pragma: no cover

    pexpect = (
        expected if isinstance(expected, basestring) else
        pformat(expected))   # pragma: no cover

    return '\n'.join(unified_diff(
        pactual.splitlines(),
        pexpect.splitlines(),
        fromfile='actual',
        tofile='expected'))  # pragma: no cover


def assert_eq(actual, expected):
    try:
        assert actual == expected
    except AssertionError:                  # pragma: no cover
        raise AssertionError(
            '\n' + diff(actual, expected))  # pragma: no cover
