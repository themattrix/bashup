import pyparsing as pp
from nose.tools import eq_, raises
from bashup.parse import variable


#
# Tests
#

def test_variable_identity_scenarios():
    scenarios = (
        '$_',
        '${_}',
        '${"}"}',
        "${'}'}",
        '${"${"${nested}"}"}',
        "${'${'${nested}'}'}",
    )

    def assert_variable_identity_scenario(scenario):
        eq_(__parse_variable(scenario), scenario)

    for s in scenarios:
        yield assert_variable_identity_scenario, s


def test_variable_failure_scenarios():
    scenarios = (
        '$',
        '${',
        '${"}"',
        "${'}'",)

    @raises(pp.ParseException)
    def assert_variable_failure_scenario(scenario):
        __parse_variable(scenario)

    for s in scenarios:
        yield assert_variable_failure_scenario, s


#
# Test Helpers
#

def __parse_variable(to_parse):
    return (
        pp.originalTextFor(variable.VARIABLE)('result')
        .leaveWhitespace()
        .parseWithTabs()
        .parseString(to_parse))['result']
