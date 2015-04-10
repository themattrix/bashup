# pylint: disable=pointless-statement, expression-not-assigned

import pyparsing as pp
from bashup.parse.name import NAME


SINGLE_QUOTED_STRING = (
    pp.QuotedString("'", multiline=True, unquoteResults=False))

CAPTURING_SUBSHELL = pp.Forward()
DOUBLE_QUOTED_STRING = pp.Forward()
VARIABLE = pp.Forward()
UNQUOTED_VALUE = pp.Forward()
VALUE = pp.Forward()

QUOTED_STRING = (
    SINGLE_QUOTED_STRING | DOUBLE_QUOTED_STRING)

SIMPLE_VARIABLE = (
    '$' + NAME)

COMPLEX_VARIABLE = (
    '${' + pp.ZeroOrMore(VALUE) + '}')

PAREN_SUBSHELL = (
    '$(' + pp.ZeroOrMore(VALUE) + ')')

BACKTICK_SUBSHELL = (
    '`' + pp.ZeroOrMore(VALUE) + '`')

CAPTURING_SUBSHELL << (
    PAREN_SUBSHELL | BACKTICK_SUBSHELL)

VARIABLE << (
    SIMPLE_VARIABLE | COMPLEX_VARIABLE)

UNQUOTED_VALUE << (
    pp.Word(pp.printables + '\n\r\t ', excludeChars='})"\\\'$`')
    | VARIABLE
    | CAPTURING_SUBSHELL)

VALUE << pp.OneOrMore(
    QUOTED_STRING | UNQUOTED_VALUE)

STRING_COMPONENT = (
    pp.White()
    | pp.Word('\\', '\\"$`', exact=2)
    | UNQUOTED_VALUE
    | pp.Word(pp.printables + '\n\r\t ', excludeChars='"'))

DOUBLE_QUOTED_STRING << pp.Combine(
    '"' + pp.ZeroOrMore(STRING_COMPONENT) + '"')

DOUBLE_QUOTED_STRING = (
    pp.originalTextFor(DOUBLE_QUOTED_STRING)
    .leaveWhitespace()
    .parseWithTabs())
