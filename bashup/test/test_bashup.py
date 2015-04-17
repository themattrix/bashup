import os
import subprocess
from glob import glob
from nose.plugins.skip import SkipTest
from nose.tools import eq_
from os.path import join
from temporary import in_temp_dir, temp_file
from textwrap import dedent
from bashup.test.common import assert_eq


# Compile some bashup and run it against multiple versions of bash. The
# versions are expected to be found in $BASH_VERSIONS_DIR. If none are
# found, or the environment variable is not set, the tests are skipped.
#
def test_compiled_bash():
    bash_binaries = __find_bash_binaries()

    if not bash_binaries:
        raise SkipTest('bash executable not found')  # pragma: no cover

    @in_temp_dir()                                   # pragma: no cover
    def assert_compiled_bash(bash_binary):           # pragma: no cover
        with temp_file(__BASHUP_STR) as in_file:     # pragma: no cover
            subprocess.check_call(args=(
                'bashup',
                '--in', in_file,
                '--out', 'hi.sh'))                   # pragma: no cover

        p = subprocess.Popen(
            args=(bash_binary, 'hi.sh'),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)                  # pragma: no cover

        stdout, _ = [
            o.decode('UTF-8').strip() for
            o in p.communicate()]                    # pragma: no cover

        assert_eq(stdout, __EXPECTED_OUTPUT)         # pragma: no cover
        eq_(p.returncode, 55)                        # pragma: no cover

    for b in bash_binaries:                          # pragma: no cover
        yield assert_compiled_bash, b                # pragma: no cover


# Compile some bashup and run it!
#
# This will obviously only work if bash exists on the system. Otherwise
# the test is skipped.
#
def test_direct_run():
    if not __is_bash_in_path():
        raise SkipTest('bash executable not found')  # pragma: no cover

    with temp_file(__BASHUP_STR) as in_file:         # pragma: no cover
        p = subprocess.Popen(
            args=('bashup', '--run', in_file),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)                  # pragma: no cover

        stdout, _ = [
            o.decode('UTF-8').strip() for
            o in p.communicate()]                    # pragma: no cover

    assert_eq(stdout, __EXPECTED_OUTPUT)             # pragma: no cover
    eq_(p.returncode, 55)                            # pragma: no cover


#
# Test Helpers
#

__BASHUP_STR = dedent("""
    #!/bin/bash

    @fn hi greeting='Hello', target='World' {
        echo "${greeting}, ${target}!$@"
    }

    # We could do this with grep, but this way is pure bash.
    @fn filter regex {
        while read line; do
            if [[ ${line} =~ ${regex} ]]; then
                echo "${line}"
            fi
        done
    }

    # Ensure that default parameters work and can be overridden.
    hi
    hi --target "Human"
    hi --greeting "Greetings"
    hi --greeting "Greetings" --target "Human"
    hi --greeting "Greetings" --target "Human" " Have" "fun!"

    # Ensure that piping between fns works.
    {
        hi --greeting "What now" --target "Human?"
        hi --greeting "Welcome" --target "Cyborg"
        hi --greeting "Hi" --target "human"

    } | filter --regex "[Hh]uman"

    exit 55
""").strip()

__EXPECTED_OUTPUT = '\n'.join((
    'Hello, World!',
    'Hello, Human!',
    'Greetings, World!',
    'Greetings, Human!',
    'Greetings, Human! Have fun!',
    'What now, Human?!',
    'Hi, human!'))


def __find_bash_binaries():
    try:
        return tuple(glob(join(os.environ['BASH_VERSIONS_DIR'], 'bash*')))
    except KeyError:  # pragma: no cover
        return ()     # pragma: no cover


def __is_bash_in_path():
    try:
        subprocess.check_call(('bash', '-c', 'true'))
        return True
    except subprocess.CalledProcessError:  # pragma: no cover
        return False                       # pragma: no cover
