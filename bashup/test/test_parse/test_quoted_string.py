import string
import pyparsing as pp
from nose.tools import eq_, raises
from bashup.parse import quoted_string
from bashup.test.test_parse.common import SimpleParseScenario


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
    obnoxious_str = (
        # """ $ """
        """$~$%$^$&"""
        """$#$*$@$-$!$?$$$_"""
        """'${_}'"${_}"$_0,!@#^&*()-+=\\\\"""
        """'}'"}"`}`$(})${}"""
        """')'")"`)`$()${)}"""
        """'`'"`"``$('`')${'`'}"""
        """\\""")

    expected_results_list = (
        [['"',
          [['${', [], '}'],
           ['$(', [], ')'],
           ['`', [], '`'],
           ['${',
            ['$', '~',
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

    to_parse = (
        '"${{}}$()``\n\r\t ${{{o}}}"'
        # '\n\r\t $({o})"'
        # '\n\r\t `{o}`"'
    ).format(o=obnoxious_str)

    results_list = (
        quoted_string
        .DOUBLE_QUOTED_STRING_UNCOMBINED
        .parseWithTabs()
        .parseString(to_parse)
        .asList())

    eq_(results_list, expected_results_list)


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
