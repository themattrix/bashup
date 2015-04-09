import string
from collections import namedtuple
from nose.tools import eq_
from bashup.parse import quoted_string


#
# Tests
#

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
    test_scenario = namedtuple('test_scenario', (
        'to_parse',
        'expected_result'))

    scenarios = (
        test_scenario(
            "'\\''",
            "'\\'"),
        test_scenario(
            "'${'}",
            "'${'"),
        test_scenario(
            "'$(')",
            "'$('"),
        test_scenario(
            "'\"'\"",
            "'\"'"),
        test_scenario(
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
        '" `` "',
        '" `echo "nested"` "',
        '''" `echo '$('` "''',
        '''" $( ) ${ } ` ` "''',
        '''" $(${`'`'`})${$(`'$('`)}`$(${'${'})` "''',
        '''" $( ${ ` ` } ) ${ $( ` ` ) } ` $( ${ } ) ` "''',
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
    test_scenario = namedtuple('test_scenario', (
        'to_parse',
        'expected_result'))

    scenarios = (
        test_scenario(
            '"${"}',
            '"${"'),
        test_scenario(
            '"$(")',
            '"$("'),
        test_scenario(
            '"`"`',
            '"`"'),
        test_scenario(
            '"\'"\'',
            '"\'"'),
        test_scenario(
            '"$(\'"\')',
            '"$(\'"'),
        test_scenario(
            '"{p}"{p}'.format(p=__RAW_ALLOWED_IN_DOUBLE_QUOTES),
            '"{p}"'.format(p=__RAW_ALLOWED_IN_DOUBLE_QUOTES)),)

    def assert_double_quoted_string_trimmed_scenario(scenario):
        eq_(__parse_double_quoted_string(scenario.to_parse),
            scenario.expected_result)

    for s in scenarios:
        yield assert_double_quoted_string_trimmed_scenario, s


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
    return (
        quoted_string
        .DOUBLE_QUOTED_STRING('result')
        .parseWithTabs()
        .parseString(to_parse))['result']
