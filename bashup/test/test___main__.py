import re
from contextlib import contextmanager
from glob import glob
from itertools import product
from mock import call, Mock
from nose.tools import eq_, raises
from temporary import temp_file
from os.path import abspath, dirname, join
from bashup.__main__ import compile_file, main, run_file
from bashup.test.common import assert_eq, captured_stdout


def test_help():
    @raises(SystemExit)
    def assert_help(argv):
        with captured_stdout() as stdout:
            try:
                main(argv)
            except SystemExit:
                __assert_in('Usage:', stdout.getvalue())
                raise
        # pylint: disable=superfluous-parens
        print(stdout.getvalue())  # pragma: no cover

    for a in (['-h'], ['--help']):
        yield assert_help, a


@raises(SystemExit)
def test_version():
    with captured_stdout() as stdout:
        try:
            main(['--version'])
        except SystemExit:
            __assert_regex_match(
                r'Bashup \d+\.\d+\.\d+',
                stdout.getvalue().strip())
            raise
    # pylint: disable=superfluous-parens
    print(stdout.getvalue())  # pragma: no cover


def test_real_file_scenarios():
    data_dir = join(dirname(abspath(__file__)), 'data')

    test_scenarios = zip(
        glob(join(data_dir, '*.bashup')),
        glob(join(data_dir, '*.sh')))

    def assert_compile_scenario(in_file, expected_file):
        with open(expected_file) as f:
            expected_stdout = f.read()
        with captured_stdout() as stdout:
            main(['--in', in_file])
        assert_eq(stdout.getvalue().strip(), expected_stdout.strip())

    for i, o in test_scenarios:
        yield assert_compile_scenario, i, o


def test_compilation_writing_to_file():
    with temp_file('to_compile') as in_file:
        with temp_file() as out_file:
            compile_file(
                in_file=in_file,
                out_file=out_file,
                compile_fn=lambda x: 'Compiled(' + x + ')')
            with open(out_file) as f:
                eq_(f.read(), 'Compiled(to_compile)')


def test_compilation_writing_to_stdout():
    with temp_file('to_compile') as in_file:
        with captured_stdout() as stdout:
            compile_file(
                in_file=in_file,
                out_file='-',
                compile_fn=lambda x: 'Compiled(' + x + ')')
        eq_(stdout.getvalue().strip(), 'Compiled(to_compile)')


def test_run_file():
    @contextmanager
    def temp_file_ctx(run_str):
        yield 'Temp(' + run_str + ')'

    with temp_file('to_compile') as to_run:
        actual = run_file(
            to_run=to_run,
            args=['one', 'two'],
            compile_fn=lambda x: 'Compiled(' + x + ')',
            run_fn=lambda x: 'Ran(' + str(x) + ')',
            temp_file_ctx=temp_file_ctx)

    eq_(actual, "Ran(('bash', 'Temp(Compiled(to_compile))', 'one', 'two'))")


def test_main_routes_to_run():
    run_flags = ('-r', '--run')

    def assert_main_routes_to_run(run_flag):
        master_mock = Mock()
        master_mock.run_fn.return_value = 'run-return'

        retval = main(
            argv=[
                run_flag, 'my-script',
                '--',
                'one', '--two', '-3', '--', 'five'],
            run_fn=master_mock.run_fn,
            compile_fn=master_mock.compile_fn)

        eq_(retval, 'run-return')
        eq_(tuple(master_mock.mock_calls), (
            call.run_fn(
                to_run='my-script',
                args=('one', '--two', '-3', '--', 'five')),))

    for f in run_flags:
        yield assert_main_routes_to_run, f


def test_main_routes_to_compile():
    in_flags = ('-i', '--in')
    out_flags = ('-o', '--out')

    def assert_main_routes_to_compile(in_flag, out_flag):
        master_mock = Mock()

        retval = main(
            argv=[in_flag, 'in-file', out_flag, 'out-file'],
            run_fn=master_mock.run_fn,
            compile_fn=master_mock.compile_fn)

        eq_(retval, 0)
        eq_(tuple(master_mock.mock_calls), (
            call.compile_fn(
                in_file='in-file',
                out_file='out-file'),))

    for i, o in product(in_flags, out_flags):
        yield assert_main_routes_to_compile, i, o


#
# Test Helpers
#

def __assert_in(subset, superset):
    assert subset in superset, (
        '{subset!r} not found in {superset!r}'.format(
            subset=subset,
            superset=superset))


def __assert_regex_match(expression, match_against):
    assert re.match(expression, match_against), (
        '{e!r} did not match {m!r}'.format(
            e=expression,
            m=match_against))
