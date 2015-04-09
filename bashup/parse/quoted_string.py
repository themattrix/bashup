# pylint: disable=pointless-statement, expression-not-assigned

import pyparsing as pp


SINGLE_QUOTED_STRING = (
    pp.QuotedString("'", multiline=True, unquoteResults=False))

NAME = pp.Word(pp.alphas + '_', pp.alphanums + '_')

CAPTURING_SUBSHELL = pp.Forward()
DOUBLE_QUOTED_STRING = pp.Forward()
VARIABLE = pp.Forward()

QUOTED_STRING = (
    SINGLE_QUOTED_STRING | DOUBLE_QUOTED_STRING)

STRING_COMPONENT = (
    pp.Literal('\\"')
    | pp.Literal('\\$')
    | pp.Literal('\\')
    | pp.Word(pp.printables + '\n\r\t ', excludeChars='\\"$`')
    | VARIABLE
    | CAPTURING_SUBSHELL
    | pp.Word(pp.printables + '\n\r\t ', excludeChars='"'))

PAREN_SUBSHELL_COMPONENT = (
    pp.Word(pp.printables + '\n\r\t ', excludeChars=')"')
    | QUOTED_STRING)

BACKTICK_SUBSHELL_COMPONENT = (
    pp.Word(pp.printables + '\n\r\t ', excludeChars='`"')
    | QUOTED_STRING)

VARIABLE_COMPONENT = (
    pp.Word(pp.printables + '\n\r\t ', excludeChars='}"')
    | QUOTED_STRING)

SIMPLE_VARIABLE = (
    '$' + NAME)

COMPLEX_VARIABLE = (
    '${' + pp.ZeroOrMore(VARIABLE_COMPONENT) + '}')

VARIABLE << (
    SIMPLE_VARIABLE | COMPLEX_VARIABLE)

PAREN_SUBSHELL = (
    '$(' + pp.ZeroOrMore(PAREN_SUBSHELL_COMPONENT) + ')')

BACKTICK_SUBSHELL = (
    '`' + pp.ZeroOrMore(BACKTICK_SUBSHELL_COMPONENT) + '`')

CAPTURING_SUBSHELL << (
    PAREN_SUBSHELL | BACKTICK_SUBSHELL)

DOUBLE_QUOTED_STRING << pp.Combine(
    '"' + pp.ZeroOrMore(STRING_COMPONENT) + '"')

DOUBLE_QUOTED_STRING = pp.originalTextFor(DOUBLE_QUOTED_STRING)
