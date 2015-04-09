import string
from nose.tools import eq_
from bashup.parse import quoted_string


def test_single_quoted_string_identity_scenarios():
    scenarios = (
        "''",
        "'  '",
        """'${'""",
        "'{p}'".format(p=string.printable.replace("'", '')),)

    def assert_single_quoted_string_scenario(scenario):
        result = (
            quoted_string
            .get_single_quoted_string()('result')
            .parseWithTabs()
            .parseString(scenario))
        eq_(result['result'], scenario)

    for s in scenarios:
        yield assert_single_quoted_string_scenario, s


# TODO: def test_single_quoted_string_trimmed_scenarios():

# TODO: def test_single_quoted_string_failure_scenarios():
