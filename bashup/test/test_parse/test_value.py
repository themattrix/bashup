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
        '\\',
        '\\\\',
        '""\'\'$~$*$_0${}$()``0aA~a@%^*)}/.:?+=-_\\\\$',)

    def assert_value_identity_scenario(scenario):
        eq_(__parse_value(scenario), scenario)

    for s in scenarios:
        yield assert_value_identity_scenario, s


def test_value_trimmed_scenarios():
    def generate_scenarios():
        for c in __INVALID_VALUE_CHARS:
            yield SimpleParseScenario(''.join(('1', c, '2')), '1')

        yield SimpleParseScenario(
            '";";1',
            '";"')
        yield SimpleParseScenario(
            "';';1",
            "';'")
        yield SimpleParseScenario(
            "`;`;1",
            "`;`")
        yield SimpleParseScenario(
            "$(;);1",
            "$(;)")
        yield SimpleParseScenario(
            "${;};1",
            "${;}")

    def assert_value_trimmed_scenario(scenario):
        eq_(__parse_value(scenario.to_parse),
            scenario.expected_result)

    for s in generate_scenarios():
        yield assert_value_trimmed_scenario, s


def test_value_failure_scenarios():
    def generate_scenarios():
        yield ''
        for c in __INVALID_VALUE_CHARS:
            yield c

    @raises(pp.ParseException)
    def assert_value_failure_scenario(scenario):
        __parse_value(scenario)

    for s in generate_scenarios():
        yield assert_value_failure_scenario, s


#
# Test Helpers
#

__INVALID_VALUE_CHARS = '"\'`\n\r\t ;,{([#!&<>|'


def __parse_value(to_parse):
    return (
        pp.originalTextFor(value.VALUE)('result')
        .leaveWhitespace()
        .parseWithTabs()
        .parseString(to_parse))['result']
