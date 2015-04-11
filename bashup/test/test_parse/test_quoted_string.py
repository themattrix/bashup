import string
import pyparsing as pp
from nose.tools import eq_, raises
from bashup.parse import quoted_string
from bashup.test.test_parse.common import SimpleParseScenario, diff


#
# Tests
#

def test_quoted_string_validation():
    quoted_string.QUOTED_STRING.validate()


def test_single_quoted_string_identity_scenarios():
    scenarios = (
        "''",
        "'  '",
        "'${'",
        "'$('",
        "'\"'",
        "'{p}'".format(p=__RAW_ALLOWED_IN_SINGLE_QUOTES),)

    def assert_single_quoted_string_identity_scenario(scenario):
        eq_(__parse_single_quoted_string(scenario), scenario)

    for s in scenarios:
        yield assert_single_quoted_string_identity_scenario, s


def test_single_quoted_string_trimmed_scenarios():
    scenarios = (
        SimpleParseScenario(
            "'\\''",
            "'\\'"),
        SimpleParseScenario(
            "'${'}",
            "'${'"),
        SimpleParseScenario(
            "'$(')",
            "'$('"),
        SimpleParseScenario(
            "'\"'\"",
            "'\"'"),
        SimpleParseScenario(
            "'{p}'{p}".format(p=__RAW_ALLOWED_IN_SINGLE_QUOTES),
            "'{p}'".format(p=__RAW_ALLOWED_IN_SINGLE_QUOTES)),)

    def assert_single_quoted_string_trimmed_scenario(scenario):
        eq_(__parse_single_quoted_string(scenario.to_parse),
            scenario.expected_result)

    for s in scenarios:
        yield assert_single_quoted_string_trimmed_scenario, s


def test_double_quoted_string_identity_scenarios():
    scenarios = (
        '""',
        '"  "',
        '" $) "',
        '" value "',
        '" $ "',
        '" $( "',
        '" ${ "',
        '" ` "',
        '" \\" "',
        '" \\\\\\" "',
        '"{p}"'.format(p=__RAW_ALLOWED_IN_DOUBLE_QUOTES),
        '" $var "',
        '" ${} "',
        '" ${_} "',
        '" ${_%%"nested"} "',
        '''" ${_%%'$('} "''',
        '" $() "',
        '" $(echo) "',
        '" $(echo "nested") "',
        '" $(echo "$(echo "nested")") "',
        '''" $(echo '$(') "''',
        '''" $('"') "''',
        '" `` "',
        '" `echo "nested"` "',
        '''" `echo '$('` "''',
        '''" $( ) ${ } ` ` "''',
        '''"$(${`'`'`})${$(`'$('`)}`$(${'${'})`"''',
        '''" $( ${ ` ` } ) ${ $( ` ` ) } ` $( ${ } ) ` "''',
        '''" $( ${ ` '`' ` } ) ${ $( ` '$(' ` ) } ` $( ${ '${' } ) ` "''',
        '''"$(')"''',
        '"\n\r\t "',
        '"$(\n\r\t )"',
        '"${\n\r\t }"',
        '"`\n\r\t `"',)

    def assert_double_quoted_string_identity_scenario(scenario):
        eq_(__parse_double_quoted_string(scenario), scenario)

    for s in scenarios:
        yield assert_double_quoted_string_identity_scenario, s


def test_double_quoted_string_trimmed_scenarios():
    scenarios = (
        SimpleParseScenario(
            '"${"}',
            '"${"'),
        SimpleParseScenario(
            '"$(")',
            '"$("'),
        SimpleParseScenario(
            '"`"`',
            '"`"'),
        SimpleParseScenario(
            '"\'"\'',
            '"\'"'),
        SimpleParseScenario(
            '"{p}"{p}'.format(p=__RAW_ALLOWED_IN_DOUBLE_QUOTES),
            '"{p}"'.format(p=__RAW_ALLOWED_IN_DOUBLE_QUOTES)),)

    def assert_double_quoted_string_trimmed_scenario(scenario):
        eq_(__parse_double_quoted_string(scenario.to_parse),
            scenario.expected_result)

    for s in scenarios:
        yield assert_double_quoted_string_trimmed_scenario, s


def test_double_quoted_string_failure_scenarios():
    scenarios = (
        '"',
        '"${""}',
        '"$("")',
        '"`""`',
        '"\\"',
        '"$(\'""\')',)

    @raises(pp.ParseException)
    def assert_double_quoted_string_failure_scenario(scenario):
        __parse_double_quoted_string(scenario)

    for s in scenarios:
        yield assert_double_quoted_string_failure_scenario, s


def test_double_quoted_string_components():
    """
    Validate the internal structure of the string.

    This test is in contrast to the rest which only care about the string as an
    opaque object. It's useful to validate that the string was parsed as
    expected instead of coincidentally working.
    """
    obnoxious_str = (
        """ $ """
        """ "\\$_" """
        """$~$%$^$&"""
        """$#$*$@$-$!$?$$$_"""
        """'${_}'"${_}"$_0,!@#^&*()-+=\\\\"""
        """'}'"}"`}`$(})${}"""
        """')'")"`)`$()${)}"""
        """'`'"`"``$('`')${'`'}"""
        """\\""")

    to_parse = (
        '"${{}}$()``\n\r\t ${{{o}}}"'
        # '\n\r\t $({o})"'
        # '\n\r\t `{o}`"'
    ).format(o=obnoxious_str)

    expected_results_list = (
        [['"',
          [['${', [], '}'],
           ['$(', [], ')'],
           ['`', [], '`'],
           ['${',
            ['$',
             ['"', ['\\$', '_'], '"'],
             '$', '~',
             '$', '%',
             '$', '^',
             '$', '&',
             ['$', '#'],
             ['$', '*'],
             ['$', '@'],
             ['$', '-'],
             ['$', '!'],
             ['$', '?'],
             ['$', '$'],
             ['$', '_'],
             "'${_}'",
             ['"', [['${', ['_'], '}']], '"'],
             ['$', '_0'],
             ',!@#^&*()-+=\\\\',
             "'}'",
             ['"', ['}'], '"'],
             ['`', ['}'], '`'],
             ['$(', ['}'], ')'],
             ['${', [], '}'],
             "')'",
             ['"', [')'], '"'],
             ['`', [')'], '`'],
             ['$(', [], ')'],
             ['${', [')'], '}'],
             "'`'",
             ['"', ['`'], '"'],
             ['`', [], '`'],
             ['$(', ["'`'"], ')'],
             ['${', ["'`'"], '}'],
             '\\'],
            '}']],
          '"']])

    parse_result = (
        quoted_string
        .DOUBLE_QUOTED_STRING_UNCOMBINED
        .parseWithTabs()
        .parseString(to_parse))

    results_list = parse_result.asList()

    try:
        eq_(results_list, expected_results_list)
    except AssertionError:  # pragma: no cover
        raise AssertionError(
            parse_result.asXML()
            + '\n\n'
            + diff(results_list, expected_results_list))  # pragma: no cover


#
# Test Helpers
#

__RAW_ALLOWED_IN_SINGLE_QUOTES = (
    string.printable
    .replace("'", ''))

__RAW_ALLOWED_IN_DOUBLE_QUOTES = (
    string.printable
    .replace('"', '')
    .replace('\\', '')
    .replace('`', '')
    .replace('$(', '')
    .replace('${', '')
    .replace('\f', '')
    .replace('\x0b', ''))


def __parse_single_quoted_string(to_parse):
    return (
        quoted_string
        .SINGLE_QUOTED_STRING('result')
        .parseWithTabs()
        .parseString(to_parse))['result']


def __parse_double_quoted_string(to_parse):
    print(
        quoted_string
        .DOUBLE_QUOTED_STRING_UNCOMBINED
        .parseWithTabs()
        .parseString(to_parse)
        .asXML())

    return (
        quoted_string
        .DOUBLE_QUOTED_STRING('result')
        .parseWithTabs()
        .parseString(to_parse))['result']
