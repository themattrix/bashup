# pylint: disable=pointless-statement, expression-not-assigned

import pyparsing as pp
from bashup.parse.name import NAME


# Enable memoization to speed up the parser.
pp.ParserElement.enablePackrat()


PRINTABLES_PLUS_WHITESPACE = pp.printables + '\n\r\t '


def any_except(exclude_chars):
    return pp.Word(PRINTABLES_PLUS_WHITESPACE, excludeChars=exclude_chars)


def enclosed(start_str, end_str):
    return pp.Group(
        pp.Literal(start_str)('start')
        + pp.Group(pp.ZeroOrMore(
            ENCLOSED
            | QUOTED_STRING
            | any_except('"\'$`' + end_str)('other')
            | pp.Literal('$')('non_variable'))('body'))
        + pp.Literal(end_str)('end'))


SINGLE_QUOTED_STRING = (
    pp.QuotedString("'", multiline=True, unquoteResults=False)
)('single_quoted_string')

DOUBLE_QUOTED_STRING_UNCOMBINED = pp.Forward()
VALUE = pp.Forward()
ENCLOSED = pp.Forward()

QUOTED_STRING = (
    SINGLE_QUOTED_STRING | DOUBLE_QUOTED_STRING_UNCOMBINED)

STRING_ESCAPED = (
    pp.Word('\\', '\\"$`', exact=2))

SPECIAL_NAME = (
    pp.Word(pp.nums + '#*@-!?_$', exact=1).leaveWhitespace())

SIMPLE_VARIABLE = pp.Group(
    pp.Literal('$')('start')
    + (NAME | SPECIAL_NAME)('name')
)('simple_variable')

EXPANDED_VARIABLE = enclosed('${', '}')('expanded_variable')
PAREN_SUBSHELL = enclosed('$(', ')')('paren_subshell')
BACKTICK_SUBSHELL = enclosed('`', '`')('backtick_subshell')

CAPTURING_SUBSHELL = (
    PAREN_SUBSHELL | BACKTICK_SUBSHELL)

VARIABLE = (
    EXPANDED_VARIABLE | SIMPLE_VARIABLE)

ENCLOSED << (
    CAPTURING_SUBSHELL | VARIABLE)

UNQUOTED_VALUE = (
    ENCLOSED | any_except('"')('unquoted_extras'))

VALUE << pp.OneOrMore(
    QUOTED_STRING | UNQUOTED_VALUE)

STRING_COMPONENT = (
    STRING_ESCAPED('string_escaped')
    | any_except('"$`\\')('string_other')
    | UNQUOTED_VALUE)

DOUBLE_QUOTED_STRING_UNCOMBINED << pp.Group(
    pp.Literal('"')('start')
    + pp.Group(pp.ZeroOrMore(STRING_COMPONENT))('body')
    + pp.Literal('"')('end'))('double_quoted_string')

DOUBLE_QUOTED_STRING = (
    pp.originalTextFor(pp.Combine(DOUBLE_QUOTED_STRING_UNCOMBINED))
    .leaveWhitespace()
    .parseWithTabs())
