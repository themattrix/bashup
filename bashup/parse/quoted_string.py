# pylint: disable=pointless-statement, expression-not-assigned

import pyparsing as pp
from bashup.parse.name import NAME


def any_except(exclude_chars):
    return pp.Word(pp.printables + '\n\r\t ', excludeChars=exclude_chars)


SINGLE_QUOTED_STRING = (
    pp.QuotedString("'", multiline=True, unquoteResults=False))

DOUBLE_QUOTED_STRING = pp.Forward()
VALUE = pp.Forward()
COMPLEX_VARIABLE_COMPONENT = pp.Forward()
PAREN_SUBSHELL_COMPONENT = pp.Forward()
BACKTICK_SUBSHELL_COMPONENT = pp.Forward()

QUOTED_STRING = (
    SINGLE_QUOTED_STRING | DOUBLE_QUOTED_STRING)

SIMPLE_VARIABLE = (
    '$' + NAME)

COMPLEX_VARIABLE = (
    '${' + pp.OneOrMore(COMPLEX_VARIABLE_COMPONENT) + '}')

PAREN_SUBSHELL = (
    '$(' + pp.ZeroOrMore(PAREN_SUBSHELL_COMPONENT) + ')')

BACKTICK_SUBSHELL = (
    '`' + pp.ZeroOrMore(BACKTICK_SUBSHELL_COMPONENT) + '`')

CAPTURING_SUBSHELL = (
    PAREN_SUBSHELL | BACKTICK_SUBSHELL)

VARIABLE = (
    SIMPLE_VARIABLE | COMPLEX_VARIABLE)

ENCLOSED = (
    VARIABLE | CAPTURING_SUBSHELL | QUOTED_STRING)

COMPLEX_VARIABLE_COMPONENT << (
    ENCLOSED | any_except('}"\'$`'))

PAREN_SUBSHELL_COMPONENT << (
    ENCLOSED | any_except(')"\'$`'))

BACKTICK_SUBSHELL_COMPONENT << (
    ENCLOSED | any_except('`"\'$'))

UNQUOTED_VALUE = (
    ENCLOSED
    | any_except('"\'$`')
    | ((pp.Word('{\\') | '$') + pp.stringEnd()))

VALUE << pp.OneOrMore(
    QUOTED_STRING | UNQUOTED_VALUE)

STRING_COMPONENT = (
    pp.White()
    | pp.Word('\\', '\\"$`', exact=2)
    | UNQUOTED_VALUE
    | any_except('"'))  # TODO: getting stuck in here

DOUBLE_QUOTED_STRING << pp.Combine(
    '"' + pp.ZeroOrMore(STRING_COMPONENT) + '"')

DOUBLE_QUOTED_STRING = (
    pp.originalTextFor(DOUBLE_QUOTED_STRING)
    .leaveWhitespace()
    .parseWithTabs())
