# pylint: disable=pointless-statement, expression-not-assigned

import pyparsing as pp
from collections import namedtuple
from bashup.parse.value import VALUE
from bashup.parse.name import NAME


class Fn(namedtuple('Fn', ('name', 'args'))):
    @classmethod
    def from_parse_result(cls, fn_parse_result):
        name = fn_parse_result['fn']['name']
        args = tuple(
            Arg.from_list(arg) for arg
            in fn_parse_result['fn'].get('parameter_list', _EMPTY).asList())
        return cls(name=name, args=args)


class Arg(namedtuple('Arg', ('name', 'value'))):
    @classmethod
    def from_list(cls, name_and_maybe_value):
        nv = name_and_maybe_value
        return cls(name=nv[0], value=nv[1] if len(nv) > 1 else None)


#
# Public Parsers
#

DEFAULT_VALUE = (
    pp.Literal('=').suppress()
    + pp.originalTextFor(VALUE)
)('value')

PARAMETER = pp.Group(
    NAME('name') + pp.Optional(DEFAULT_VALUE)
)('parameter')

PARAMETER_LIST = (
    pp.delimitedList(PARAMETER)
)('parameter_list')

FN = pp.Group(
    pp.Literal('@fn').suppress()
    + NAME('name')
    + pp.Optional(PARAMETER_LIST)
    + pp.Literal('{').suppress()
)('fn')


#
# Private Helpers
#

class _Empty(object):  # pylint: disable=too-few-public-methods
    @staticmethod
    def asList():      # pylint: disable=invalid-name
        return []


_EMPTY = _Empty()
