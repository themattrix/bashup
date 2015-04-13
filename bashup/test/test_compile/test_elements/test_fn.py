from textwrap import dedent
from bashup.parse.fn import Fn, Arg
from bashup.compile.elements import fn
from bashup.test.common import diff


#
# Tests
#

def test_compile_fn_spec_to_bash_without_args():
    expected = dedent("""
        #
        # usage: hello [ARGS]
        #
        function hello() {
    """).strip()

    actual = fn.compile_fn_spec_to_bash(fn_spec=Fn(
        name='hello',
        args=()))

    __assert_eq(actual, expected)


def test_compile_fn_spec_to_bash_with_args():
    expected = dedent("""
        #
        # usage: enable_ramdisk --size <SIZE> [--path <PATH>] [ARGS]
        #
        function enable_ramdisk() {
            local size
            local size__set=0
            local path='/ramdisk'
            local args=()
            local i

            for ((i = 1; i < $#; i++)); do
                if [ "${!i}" == "--size" ]; then
                    ((i++))
                    size=${!i}
                    size__set=1
                elif [ "${!i}" == "--path" ]; then
                    ((i++))
                    path=${!i}
                else
                    args+=("${!i}")
                fi
            done

            if [ ${size__set} -eq 0 ]; then
                echo "[ERROR] The --size parameter must be given."
                return 1
            fi

            __enable_ramdisk "${size}" "${path}" "${args[@]}"
        }

        function __enable_ramdisk() {
            local size=${1}
            local path=${2}
            shift 2

    """).lstrip()

    actual = fn.compile_fn_spec_to_bash(fn_spec=Fn(
        name='enable_ramdisk',
        args=(Arg(name='size', value=None),
              Arg(name='path', value="'/ramdisk'"))))

    __assert_eq(actual, expected)


def test_compile_fns_to_bash_single_fn_without_args():
    expected = dedent("""
        #
        # usage: hello [ARGS]
        #
        function hello() {
            echo "hello!"
        }
    """).strip()

    actual = fn.compile_fns_to_bash(bashup_str=dedent("""
        @fn hello {
            echo "hello!"
        }
    """).strip())

    __assert_eq(actual, expected)


#
# Test Helpers
#

def __assert_eq(actual, expected):
    try:
        assert actual == expected
    except AssertionError:                  # pragma: no cover
        raise AssertionError(
            '\n' + diff(actual, expected))  # pragma: no cover
