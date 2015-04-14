# pylint: disable=pointless-statement, expression-not-assigned

import pyparsing as pp
from bashup.parse.name import NAME


# Enable memoization to speed up the parser.
pp.ParserElement.enablePackrat()


#
# Public Constants
#

PRINTABLES_PLUS_WHITESPACE = pp.printables + '\n\r\t '


#
# Private Parser Creators
#

def __any_except(exclude_chars):
    return pp.Word(PRINTABLES_PLUS_WHITESPACE, excludeChars=exclude_chars)


def __enclosed(start_str, end_str):
    def __generate_match_first():
        yield PAREN_SUBSHELL
        if start_str != '`':
            yield BACKTICK_SUBSHELL
        yield VARIABLE
        yield QUOTED_STRING
        yield __any_except('"\'$`' + end_str)('other')
        yield pp.Literal('$')('non_variable')

    match_first = pp.MatchFirst(list(__generate_match_first()))

    return pp.Group(
        pp.Literal(start_str)('start') +
        pp.Group(pp.ZeroOrMore(match_first))('body') +
        pp.Literal(end_str)('end'))


def __value(quoted):
    return (
        CAPTURING_SUBSHELL |
        VARIABLE |
        __any_except('"' if quoted else '"\'$`\n\r\t ;,{([#!&<>|')(
            'quoted_extras' if quoted else 'unquoted_extras'))


#
# Forward-Declarations
#

DOUBLE_QUOTED_STRING_UNCOMBINED = pp.Forward()
VARIABLE = pp.Forward()
BACKTICK_SUBSHELL = pp.Forward()
PAREN_SUBSHELL = pp.Forward()


#
# Public Parsers
#

SINGLE_QUOTED_STRING = (
    pp.QuotedString("'", multiline=True, unquoteResults=False)
)('single_quoted_string')

QUOTED_STRING = (SINGLE_QUOTED_STRING | DOUBLE_QUOTED_STRING_UNCOMBINED)
STRING_ESCAPED = pp.Word('\\', '\\"$`', exact=2)
SPECIAL_NAME = pp.Word(pp.nums + '#*@-!?_$', exact=1).leaveWhitespace()

SIMPLE_VARIABLE = pp.Group(
    pp.Literal('$')('start') +
    (NAME | SPECIAL_NAME)('name')
)('simple_variable')

EXPANDED_VARIABLE = __enclosed('${', '}')('expanded_variable')
PAREN_SUBSHELL << __enclosed('$(', ')')('paren_subshell')
BACKTICK_SUBSHELL << __enclosed('`', '`')('backtick_subshell')
CAPTURING_SUBSHELL = (PAREN_SUBSHELL | BACKTICK_SUBSHELL)
VARIABLE << (EXPANDED_VARIABLE | SIMPLE_VARIABLE)

STRING_COMPONENT = (
    STRING_ESCAPED('string_escaped') |
    __any_except('"$`\\')('string_other') |
    __value(quoted=True))

DOUBLE_QUOTED_STRING_UNCOMBINED << pp.Group(
    pp.Literal('"')('start') +
    pp.Group(pp.ZeroOrMore(STRING_COMPONENT))('body') +
    pp.Literal('"')('end'))('double_quoted_string')

DOUBLE_QUOTED_STRING = (
    pp.originalTextFor(pp.Combine(DOUBLE_QUOTED_STRING_UNCOMBINED))
    .leaveWhitespace()
    .parseWithTabs())

VALUE = pp.Group(pp.OneOrMore(
    SINGLE_QUOTED_STRING |
    DOUBLE_QUOTED_STRING |
    __value(quoted=False) |
    ('$' + (pp.StringEnd() | pp.LineEnd() | ~SPECIAL_NAME))))
