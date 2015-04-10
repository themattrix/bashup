import pyparsing as pp
from nose.tools import eq_, raises
from bashup.parse import value


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
        '\\\\',)

    def assert_value_identity_scenario(scenario):
        eq_(__parse_value(scenario), scenario)

    for s in scenarios:
        yield assert_value_identity_scenario, s


def test_value_failure_scenarios():
    scenarios = (
        '',)

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
