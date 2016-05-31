import subprocess
import os
import itertools
import textwrap

import pathlib2 as pathlib
import pytest
import temporary

from .. import test


# Compile some bashup and run it against multiple versions of bash. The versions are expected to be found in
# $BASH_VERSIONS_DIR. If none are found, or the environment variable is not set, the tests are skipped.
def test_compiled_bash():  # pragma: no cover
    bash_binaries = __find_bash_binaries()

    if not bash_binaries:
        pytest.skip('bash executable not found')

    for bash_binary in bash_binaries:
        yield __assert_compiled_bash, bash_binary, __BASHUP_STR, __EXPECTED_OUTPUT, 55


# Compile some bashup and run it! This will only work if bash exists on the system. Otherwise the test is skipped.
def test_direct_run():  # pragma: no cover
    if not __is_bash_in_path():
        pytest.skip('bash executable not found')

    if not __is_bashup_in_path():
        pytest.skip('bashup executable not found')

    with temporary.temp_file(__BASHUP_STR) as in_file:
        p = subprocess.Popen(
            args=('bashup', '--run', str(in_file)),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

        stdout, _ = [o.decode('utf-8').strip() for o in p.communicate()]

        test.assert_eq(stdout, __EXPECTED_OUTPUT)
    assert p.returncode == 55


def test_docopt():  # pragma: no cover
    bash_binaries = __find_bash_binaries()

    if not bash_binaries:
        pytest.skip('bash executable not found')

    docopt_str = textwrap.dedent("""
        #!/bin/bash
        #
        # Naval Fate.
        #
        # Usage:
        #   naval_fate ship new <name>...
        #   naval_fate ship <name> move <x> <y> [--speed=<kn>]
        #   naval_fate ship shoot <x> <y>
        #   naval_fate mine (set|remove) <x> <y> [--moored|--drifting]
        #   naval_fate -h | --help
        #   naval_fate --version
        #
        # Options:
        #   -h --help     Show this screen.
        #   --version     Show version.
        #   --speed=<kn>  Speed in knots [default: 10].
        #   --moored      Moored (anchored) mine.
        #   --drifting    Drifting mine.
        #
        # Version:
        #   Naval Fate 2.0

        args=("${@}")

        printf '%s\n' 'args=('
        for i in "${!args[@]}"; do
            printf '    [%q]=%q\n' "${i}" "${args[${i}]}"
        done
        printf ')\n'
    """).strip()

    expected_return_code = 0

    # @fn main {
    #     @echo @args
    # }
    #
    # @sourced || {
    #     @docopt
    #     main
    # }

    args_and_expected_output = (
        (('ship', 'new', '  ship  name'),
         textwrap.dedent("""
            args=(
                [0]=ship
                [1]=new
                [2]=\\ \\ ship\\ \\ name
            )
         """).strip()),

        (('ship', '  ship  name', 'move', '-100', '200', '--speed=5.5'),
         textwrap.dedent("""
            args=(
                [0]=ship
                [1]=\\ \\ ship\\ \\ name
                [2]=move
                [3]=-100
                [4]=200
                [5]=--speed=5.5
            )
         """).strip()),
    )

    parameters = itertools.product(bash_binaries, args_and_expected_output)

    for bash_binary, (script_args, expected_output) in parameters:
        yield __assert_compiled_bash, bash_binary, docopt_str, expected_output, expected_return_code, script_args


#
# Test Helpers
#

__BASHUP_STR = textwrap.dedent("""
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
    hi --target="Human"
    hi --greeting="Greetings"
    hi --greeting="Greetings" --target="Human"
    hi --greeting="Greetings" --target="Human" " Have" "fun!"

    # Ensure that piping between fns works.
    {
        hi --greeting="What now" --target="Human?"
        hi --greeting="Welcome" --target="Cyborg"
        hi --greeting="Hi" --target="human"

    } | filter --regex="[Hh]uman"

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
        return tuple((str(p) for p in pathlib.Path(os.environ['BASH_VERSIONS_DIR']).glob('bash*')))
    except KeyError:  # pragma: no cover
        return ()     # pragma: no cover


def __is_bash_in_path():
    try:
        subprocess.check_call(('bash', '-c', ':'))
        return True                                     # pragma: no cover
    except (subprocess.CalledProcessError, OSError):    # pragma: no cover
        return False                                    # pragma: no cover


def __is_bashup_in_path():
    try:
        subprocess.check_call(('bashup', '--version'))
        return True                                     # pragma: no cover
    except (subprocess.CalledProcessError, OSError):    # pragma: no cover
        return False                                    # pragma: no cover


@temporary.in_temp_dir()
def __assert_compiled_bash(
        bash_binary,
        bashup_str,
        expected_output,
        expected_return_code,
        script_args=()):                                # pragma: no cover

    with temporary.temp_file(bashup_str) as in_file:
        subprocess.check_call(args=(
            'bashup',
            '--in', str(in_file),
            '--out', 'out.sh'))

    p = subprocess.Popen(
        args=(bash_binary, 'out.sh') + tuple(script_args),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    stdout, _ = [o.decode('UTF-8').strip() for o in p.communicate()]

    test.assert_eq(stdout, expected_output)
    assert p.returncode == expected_return_code
