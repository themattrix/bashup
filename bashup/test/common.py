from difflib import unified_diff
from pprint import pformat


def diff(actual, expected):
    return '\n'.join(unified_diff(
        pformat(actual).splitlines(),
        pformat(expected).splitlines(),
        fromfile='actual',
        tofile='expected'))  # pragma: no cover
