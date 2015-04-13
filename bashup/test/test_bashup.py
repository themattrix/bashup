import subprocess
from nose.plugins.skip import SkipTest
from nose.tools import eq_
from temporary import in_temp_dir, temp_file
from textwrap import dedent
from bashup.test.common import assert_eq


@in_temp_dir()
def test_compiled_bash():
    """
    Compile some bashup and run it!

    This will obviously only work if bash exists on the system. Otherwise,
    the test is skipped.
    """
    __ensure_bash_exists()

    bashup_str = dedent("""
        @fn hi greeting='hello', target='world' {
            echo "${greeting}, ${target}!"
        }

        hi >&2
        hi --greeting "greetings" --target "human"

        exit 55
    """).strip()

    with temp_file(bashup_str) as in_file:
        __bashup('--in', in_file, '--out', 'hi.sh')

    p = subprocess.Popen(
        args=('bash', 'hi.sh'),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    stdout, stderr = [o.decode('UTF-8').strip() for o in p.communicate()]

    assert_eq(stdout, 'greetings, human!')
    assert_eq(stderr, 'hello, world!')
    eq_(p.returncode, 55)


#
# Test Helpers
#

def __bashup(*argv):
    subprocess.check_call(args=('bashup',) + tuple(argv))


def __ensure_bash_exists():
    try:
        subprocess.check_call(('bash', '-c', 'true'))
    except subprocess.CalledProcessError:            # pragma: no cover
        raise SkipTest('bash executable not found')  # pragma: no cover
