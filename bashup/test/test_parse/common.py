from collections import namedtuple
from difflib import context_diff
from pprint import pformat


SimpleParseScenario = namedtuple('SimpleParseScenario', (
    'to_parse',
    'expected_result'))


def diff(actual, expected):
    return '\n'.join(context_diff(
        pformat(actual).splitlines(),
        pformat(expected).splitlines(),
        fromfile='actual',
        tofile='expected'))  # pragma: no cover
