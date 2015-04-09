import pyparsing as pp


#
# Private Helpers
#

# pylint: disable=pointless-statement, expression-not-assigned
def __create_double_quoted_string():
    name = pp.Word(pp.alphas + '_', pp.alphanums + '_')

    capturing_subshell = pp.Forward()
    double_quoted_string = pp.Forward()
    variable = pp.Forward()

    quoted_string = (
        SINGLE_QUOTED_STRING | double_quoted_string)

    string_component = (
        pp.Literal('\\"')
        | pp.Literal('\\$')
        | pp.Literal('\\')
        | pp.Word(pp.printables + '\n\r\t ', excludeChars='\\"$`')
        | variable
        | capturing_subshell
        | pp.Word(pp.printables + '\n\r\t ', excludeChars='"')
    )

    paren_subshell_component = (
        pp.Word(pp.printables + '\n\r\t ', excludeChars=')"')
        | quoted_string)

    backtick_subshell_component = (
        pp.Word(pp.printables + '\n\r\t ', excludeChars='`"')
        | quoted_string)

    variable_component = (
        pp.Word(pp.printables + '\n\r\t ', excludeChars='}"')
        | quoted_string)

    simple_variable = (
        '$' + name)

    complex_variable = (
        '${' + pp.ZeroOrMore(variable_component) + '}')

    variable << (
        simple_variable | complex_variable)

    paren_subshell = (
        '$(' + pp.ZeroOrMore(paren_subshell_component) + ')')

    backtick_subshell = (
        '`' + pp.ZeroOrMore(backtick_subshell_component) + '`')

    capturing_subshell << (
        paren_subshell | backtick_subshell)

    double_quoted_string << pp.Combine(
        '"' + pp.ZeroOrMore(string_component) + '"')

    return pp.originalTextFor(double_quoted_string)


#
# Public Parsers
#

SINGLE_QUOTED_STRING = (
    pp.QuotedString("'", multiline=True, unquoteResults=False))

DOUBLE_QUOTED_STRING = (
    __create_double_quoted_string())

QUOTED_STRING = (
    SINGLE_QUOTED_STRING | DOUBLE_QUOTED_STRING)
