import pyparsing as pp
from nose.tools import eq_, raises
from bashup.parse import value
from bashup.test.test_parse.common import SimpleParseScenario


#
# Tests
#

def test_value_identity_scenarios():
    scenarios = (
        '3',
        '$',
        ')',
        '))',
        '$))3',
        '}',
        '}}',
        '$}}3',
        '{',
        '{{',
        '3{{$',
        '\\',
        '\\\\',
        '''$~$*$_0${}$()``''""a,Z\\\\$''',
        ''' $~ $* $_0 ${} $() `` '' "" a,Z\\\\$ ''',)

    def assert_value_identity_scenario(scenario):
        eq_(__parse_value(scenario), scenario)

    for s in scenarios:
        yield assert_value_identity_scenario, s


def test_value_trimmed_scenarios():
    scenarios = (
        SimpleParseScenario(
            '1;2',
            '1'),
        SimpleParseScenario(
            '1\n2',
            '1'),
        SimpleParseScenario(
            '1\r2',
            '1'),
        SimpleParseScenario(
            '";";1',
            '";"'),
        SimpleParseScenario(
            "';';1",
            "';'"),
        SimpleParseScenario(
            "`;`;1",
            "`;`"),
        SimpleParseScenario(
            "$(;);1",
            "$(;)"),
        SimpleParseScenario(
            "${;};1",
            "${;}"),)

    def assert_value_trimmed_scenario(scenario):
        eq_(__parse_value(scenario.to_parse),
            scenario.expected_result)

    for s in scenarios:
        yield assert_value_trimmed_scenario, s


def test_value_failure_scenarios():
    scenarios = (
        '',
        ';',)

    @raises(pp.ParseException)
    def assert_value_failure_scenario(scenario):
        __parse_value(scenario)

    for s in scenarios:
        yield assert_value_failure_scenario, s


#
# Test Helpers
#

def __parse_value(to_parse):
    return (
        pp.originalTextFor(value.VALUE)('result')
        .leaveWhitespace()
        .parseWithTabs()
        .parseString(to_parse))['result']
