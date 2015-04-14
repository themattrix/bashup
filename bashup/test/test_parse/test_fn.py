import pyparsing as pp
from nose.tools import eq_, raises
from bashup.parse.fn import FN, FnSpec, ArgSpec
from bashup.test.common import diff
from bashup.test.test_parse.common import SimpleParseScenario


def test_fn_success_scenarios():
    scenarios = (
        SimpleParseScenario(
            '@fn hello {',
            FnSpec(name='hello',
                   args=())),
        SimpleParseScenario(
            '@fn\n\r\t hello\n\r\t {',
            FnSpec(name='hello',
                   args=())),
        SimpleParseScenario(
            '@fn hello arg {',
            FnSpec(name='hello',
                   args=(ArgSpec(name='arg', value=None),))),
        SimpleParseScenario(
            '@fn hello arg=value {',
            FnSpec(name='hello',
                   args=(ArgSpec(name='arg', value='value'),))),
        SimpleParseScenario(
            '@fn hello arg=9000 {',
            FnSpec(name='hello',
                   args=(ArgSpec(name='arg', value='9000'),))),
        SimpleParseScenario(
            '@fn hello arg=9000over {',
            FnSpec(name='hello',
                   args=(ArgSpec(name='arg', value='9000over'),))),
        SimpleParseScenario(
            '@fn hello arg1=value1, arg2=value2 {',
            FnSpec(name='hello',
                   args=(ArgSpec(name='arg1', value='value1'),
                         ArgSpec(name='arg2', value='value2')))),
        SimpleParseScenario(
            '@fn h a1=v1, a2, a3=v3, a4 {',
            FnSpec(name='h',
                   args=(ArgSpec(name='a1', value='v1'),
                         ArgSpec(name='a2', value=None),
                         ArgSpec(name='a3', value='v3'),
                         ArgSpec(name='a4', value=None)))),
        SimpleParseScenario(
            '@fn h a1=v1,a2,a3=v3,a4{',
            FnSpec(name='h',
                   args=(ArgSpec(name='a1', value='v1'),
                         ArgSpec(name='a2', value=None),
                         ArgSpec(name='a3', value='v3'),
                         ArgSpec(name='a4', value=None)))),
        SimpleParseScenario(
            '''@fn h a1='v1a, v1b', a2, a3="${v3a}, ${v3b}" {''',
            FnSpec(name='h',
                   args=(ArgSpec(name='a1', value="'v1a, v1b'"),
                         ArgSpec(name='a2', value=None),
                         ArgSpec(name='a3', value='"${v3a}, ${v3b}"')))),
        SimpleParseScenario(
            '''@fn h a="", b='' {''',
            FnSpec(name='h',
                   args=(ArgSpec(name='a', value='""'),
                         ArgSpec(name='b', value="''")))),
        SimpleParseScenario(
            '''@fn h a='"', b='"' {''',
            FnSpec(name='h',
                   args=(ArgSpec(name='a', value="'\"'"),
                         ArgSpec(name='b', value="'\"'")))),
        SimpleParseScenario(
            '''@fn h a="'", b="'" {''',
            FnSpec(name='h',
                   args=(ArgSpec(name='a', value='"\'"'),
                         ArgSpec(name='b', value='"\'"')))),
        SimpleParseScenario(
            '''@fn h a="${PATH//"/bin"/"/bun"}", b="\\"" {''',
            FnSpec(name='h',
                   args=(ArgSpec(name='a', value='"${PATH//"/bin"/"/bun"}"'),
                         ArgSpec(name='b', value='"\\""')))),
        SimpleParseScenario(
            '''@fn h a=""''$~$*$_0${}$()``0aA~a@%^*)}/.:?+=-_\\\\$ {''',
            FnSpec(name='h',
                   args=(ArgSpec(name='a', value=(
                       '""\'\'$~$*$_0${}$()``0aA~a@%^*)}/.:?+=-_\\\\$')),))),)

    def assert_fn_scenario(scenario):
        parse_result = FN.parseWithTabs().parseString(scenario.to_parse)
        actual_result = FnSpec.from_parse_result(parse_result)

        try:
            eq_(actual_result, scenario.expected_result)
        except AssertionError:  # pragma: no cover
            raise AssertionError(
                parse_result.asXML() +
                '\n\n' +
                diff(actual_result, scenario.expected_result)
            )  # pragma: no cover

    for s in scenarios:
        yield assert_fn_scenario, s


def test_fn_failure_scenarios():
    scenarios = (
        '@fn {',
        '@fn arg=value {',
        '@fn name arg={',
        '@fn name arg= {',
        '@fn name arg={} {',)

    @raises(pp.ParseException)
    def assert_fn_failure_scenario(scenario):
        result = FN.parseWithTabs().parseString(scenario)
        # pylint: disable=superfluous-parens
        print(result.asXML())  # pragma: no cover

    for s in scenarios:
        yield assert_fn_failure_scenario, s
