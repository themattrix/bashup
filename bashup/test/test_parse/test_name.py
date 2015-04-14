import string
import pyparsing as pp
from nose.tools import eq_, raises
from bashup.parse import name


#
# Tests
#

def test_name_identity_scenarios():
    def generate_scenarios():
        for c in __VALID_FIRST:
            yield c
        for c in __VALID_SECOND:
            yield '_' + c

    def assert_name_identity_scenario(scenario):
        eq_(__parse_name(scenario), scenario)

    for s in generate_scenarios():
        yield assert_name_identity_scenario, s


def test_name_failure_scenarios():
    def generate_scenarios():
        for c in __INVALID_FIRST:
            yield c
        for c in __INVALID_SECOND:
            yield '_' + c

    @raises(pp.ParseException)
    def assert_name_failure_scenario(scenario):
        __parse_name(scenario)

    for s in generate_scenarios():
        yield assert_name_failure_scenario, s


#
# Test Helpers
#

__VALID_FIRST = (
    string.ascii_letters +
    '_')

__VALID_SECOND = (
    string.ascii_letters +
    string.digits +
    '_')

__INVALID_FIRST = (
    string.digits +
    string.whitespace +
    string.punctuation.replace('_', ''))

__INVALID_SECOND = (
    string.whitespace +
    string.punctuation.replace('_', ''))


def __parse_name(to_parse):
    return (
        (pp.StringStart() + name.NAME('result') + pp.StringEnd())
        .leaveWhitespace()
        .parseWithTabs()
        .parseString(to_parse))['result']
