import re
import sys
from contextlib import contextmanager
from glob import glob
from nose.tools import eq_, raises
from temporary import temp_file
from os.path import abspath, dirname, join
from bashup.__main__ import compilation, main
from bashup.test.common import assert_eq


try:
    from cStringIO import StringIO
except ImportError:          # pragma: no cover
    from io import StringIO  # pragma: no cover


def test_help():
    @raises(SystemExit)
    def assert_help(argv):
        with __captured_stdout() as stdout:
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
    with __captured_stdout() as stdout:
        try:
            main(['--version'])
        except SystemExit:
            __assert_regex_match(
                r'Bashup \d+\.\d+\.\d+',
                stdout.getvalue().strip())
            raise
    # pylint: disable=superfluous-parens
    print(stdout.getvalue())  # pragma: no cover


def test_compilation_scenarios():
    data_dir = join(dirname(abspath(__file__)), 'data')

    test_scenarios = zip(
        glob(join(data_dir, '*.bashup')),
        glob(join(data_dir, '*.sh')))

    def assert_compile_scenario(in_file, expected_file):
        with open(expected_file) as f:
            expected_stdout = f.read()
        with __captured_stdout() as stdout:
            main(['--in', in_file])
        assert_eq(stdout.getvalue().strip(), expected_stdout.strip())

    for i, o in test_scenarios:
        yield assert_compile_scenario, i, o


def test_compilation_writing_to_file():
    with temp_file('to_compile') as in_file:
        with temp_file() as out_file:
            compilation(
                args={'--in': in_file, '--out': out_file},
                compile_fn=lambda x: 'Compiled(' + x + ')')
            with open(out_file) as f:
                eq_(f.read(), 'Compiled(to_compile)')


#
# Test Helpers
#

@contextmanager
def __captured_stdout():
    old_out = sys.stdout
    try:
        sys.stdout = StringIO()
        yield sys.stdout
    finally:
        sys.stdout = old_out


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
