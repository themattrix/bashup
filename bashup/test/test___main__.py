import contextlib
import itertools
import re

import mock
import pathlib2 as pathlib
import pytest
import temporary

from .. import __main__
from .. import test


DATA_DIR = pathlib.Path(__file__).parent / 'data'


@pytest.mark.parametrize('argv', (['-h'], ['--help']))
def test_help(argv):
    with pytest.raises(SystemExit):
        with test.captured_stdout() as stdout:
            try:
                __main__.main(argv)
            except SystemExit:
                __assert_in('Usage:', stdout.getvalue())
                raise
        # pylint: disable=superfluous-parens
        print(stdout.getvalue())  # pragma: no cover


def test_version():
    with pytest.raises(SystemExit):
        with test.captured_stdout() as stdout:
            try:
                __main__.main(['--version'])
            except SystemExit:
                __assert_regex_match(
                    r'Bashup \d+\.\d+\.\d+',
                    stdout.getvalue().strip())
                raise
        # pylint: disable=superfluous-parens
        print(stdout.getvalue())  # pragma: no cover


@pytest.mark.parametrize('in_file,expected_file', zip(
    DATA_DIR.glob('*.bashup'),
    DATA_DIR.glob('*.sh'),
))
def test_real_file_scenarios(in_file, expected_file):
    with expected_file.open() as f:
        expected_stdout = f.read()

    with test.captured_stdout() as stdout:
        __main__.main(['--in', str(in_file)])

        test.assert_eq(stdout.getvalue().strip(), expected_stdout.strip())


def test_compilation_writing_to_file():
    with temporary.temp_file('to_compile') as in_file:
        with temporary.temp_file() as out_file:
            __main__.compile_file(
                in_file=in_file,
                out_file=out_file,
                compile_fn=lambda x: 'Compiled(' + x + ')')
            with open(str(out_file)) as f:
                assert f.read() == 'Compiled(to_compile)'


def test_compilation_writing_to_stdout():
    with temporary.temp_file('to_compile') as in_file:
        with test.captured_stdout() as stdout:
            __main__.compile_file(
                in_file=in_file,
                out_file='-',
                compile_fn=lambda x: 'Compiled(' + x + ')')
        assert stdout.getvalue().strip() == 'Compiled(to_compile)'


def test_run_file():
    @contextlib.contextmanager
    def temp_file_ctx(run_str):
        yield 'Temp(' + run_str + ')'

    with temporary.temp_file('to_compile') as to_run:
        actual = __main__.run_file(
            to_run=to_run,
            args=['one', 'two'],
            compile_fn=lambda x: 'Compiled(' + x + ')',
            run_fn=lambda x: 'Ran(' + str(x) + ')',
            temp_file_ctx=temp_file_ctx)

    assert actual == "Ran(('bash', 'Temp(Compiled(to_compile))', 'one', 'two'))"


@pytest.mark.parametrize('run_flag', ('-r', '--run'))
def test_main_routes_to_run(run_flag):
    master_mock = mock.Mock()
    master_mock.run_fn.return_value = 'run-return'

    retval = __main__.main(
        argv=[run_flag, 'my-script', '--', 'one', '--two', '-3', '--', 'five'],
        run_fn=master_mock.run_fn,
        compile_fn=master_mock.compile_fn)

    assert retval == 'run-return'
    assert tuple(master_mock.mock_calls) == (
        mock.call.run_fn(
            to_run='my-script',
            args=('one', '--two', '-3', '--', 'five')),)


@pytest.mark.parametrize('in_flag,out_flag', itertools.product(('-i', '--in'), ('-o', '--out')))
def test_main_routes_to_compile(in_flag, out_flag):
    master_mock = mock.Mock()

    retval = __main__.main(
        argv=[in_flag, 'in-file', out_flag, 'out-file'],
        run_fn=master_mock.run_fn,
        compile_fn=master_mock.compile_fn)

    assert retval == 0
    assert tuple(master_mock.mock_calls) == (
        mock.call.compile_fn(
            in_file='in-file',
            out_file='out-file'),)


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
