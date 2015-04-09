# from bashup.parse import fn
from bashup.test.test_parse.common import SimpleParseScenario


def test_fn_scenarios():
    scenarios = (
        SimpleParseScenario(
            '',
            ''),
    )

    def assert_fn_scenario(scenario):
        assert scenario

    for s in scenarios:
        yield assert_fn_scenario, s
