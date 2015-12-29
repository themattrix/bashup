Planned Constructs
==================

Bash Options
------------

This will be inserted at the top of every script (including the comments):

.. code:: bash

    set -o errexit      # exit immediately if a command fails
    set -o pipefail     # ...including commands in a pipeline
    set -o nounset      # use of undefined variables is an error
    set -o noclobber    # prevent redirection from overwriting files
    shopt -o nullglob   # expand an unmatching glob pattern to a null string
    shopt -o dotglob    # glob matches files starting with a dot


Safer Echo
----------

.. code:: bash

    # print a string
    @echo "--help"

    # print an array
    @echo @args


Generated bash:

.. code:: bash

    # print a string
    printf '%s\n' "--help"

    # print an array
    printf '%s\n' 'args=('
    for i in "${!args[@]}"; do
        printf '  [%q]=%q\n' "${i}" "${args[${i}]}"
    done
    printf ')\n'


Trap and Re-Raise Signal
------------------------

  Inspired by `Proper handling of SIGINT/SIGQUIT <http://www.cons.org/cracauer/sigint.html>`

.. code:: bash

    @trap INT QUIT {
        ...
    }


A well-behaved script should re-raise every signal that it can.
To do this properly, the script must reset the signal and then kill itself
with that same signal. Since there's no way to determine which signal was
raised, there must be a separate handler for each so that the correct signal
is re-raised.

.. code:: bash

    __INT_QUIT_handler() {
        ...
    }

    trap '__INT_QUIT_handler "$@"; trap INT; kill -INT $$' INT
    trap '__INT_QUIT_handler "$@"; trap QUIT; kill -QUIT $$' QUIT


Note that for clean-up tasks, a context manager should generally be used instead.


Context Managers
----------------

  Inspired by `Python's @contextmanager decorator <https://docs.python.org/3.4/library/contextlib.html#contextlib.contextmanager>`_.

A context manager is responsible for running some code when entering and
exiting a block. The exiting code is always run, even when the block is
terminated early. This is especially useful for clean-up tasks, like deleting
a temporary directory. For example, the following bashup code would define
just such a context manager:

.. code:: bash

    @ctx mktemp {
        local tmp=$(mktemp "$@")
        @yield "${tmp}"
        rm -rf "${tmp}"
    }


The context manager could then be used as follows:

.. code:: bash

    # multi-line version
    @with(mktemp -d) as tmp {
        ...
    }

    # single-line version
    ... @with(mktemp -d) as tmp


The generated bash would look something like this:

.. code:: bash

    with_mktemp() (
        local body_fn=${1}; shift
        local tmp=$(mktemp "$@")

        exit_ctx() {
            rm -f "${tmp}"
        }

        trap exit_ctx EXIT

        "${body_fn}" "${tmp}"
    )

    ...

    ctx_0() {
        local tmp=${1}
        ...
    }

    with_mktemp ctx_0 -d


Note that the body of the context ends up being evaluated in a subshell. If
this is unacceptable, consider using a *decorator* instead.


Decorators
----------

Like Python decorators, but evaluated every time the function is called.

.. code:: bash

    # Decorator to temporarily toggle off exiting on non-zero exit statuses.
    @fn ignore_failure {
        set +e
        "$@" || :
        set -e
    }

    # Print a message with the name and arguments of the decorated fn.
    @fn show_args {
        echo ">>> $@"
        "$@"
    }

    @ignore_failure
    @show_args
    @fn enable_ramdisk size, path='/ramdisk' {
        ...
    }


Equivalent bash:

.. code:: bash

    ignore_failure() {
        set +e
        "$@" || :
        set -e
    }

    show_args() {
        echo ">>> $@"
        "$@"
    }

    enable_ramdisk() {
        ...
    }

    eval "$(echo "enable_ramdisk() {"; )"

    enable_ramdisk_0() {
        show_args enable_ramdisk_orig "$@"
    }

    # TODO: finish this


https://stackoverflow.com/questions/1203583/how-do-i-rename-a-bash-function


Decorators can also be used to decorate a single line:

.. code:: bash

    false @ignore_failure


Equivalent bash:

.. code:: bash

    ignore_failure false


The bash is actually (one character) shorter, but I think the bashup reads better.


Aliases
-------

Aliases would be useful for keeping your bashup code as
`DRY <http://en.wikipedia.org/wiki/Don%27t_repeat_yourself>`_ as possible.
They'd have to be evaluated before any other constructs.

For example, let's say you've defined a context manager which creates a
temporary file with a longer-than-normal name:

.. code:: bash

    @mytmp = @with(mktemp tmp.XXXXXXXXXXXXXXXXXXXXXXXXXX)


The alias can then be treated as a literal text substitution:

.. code:: bash

    @mytmp as tmp {
        ...
    }


Macros
------

Macros are aliases that can take options. Or, more accurately - aliases are
just a special case of macros that take no options.

Here's a similar example to above:

.. code:: bash

    @mytmp(extra) = @with(mktemp @extra tmp.XXXXXXXXXXXXXXXXXXXXXXXXXX)


.. code:: bash

    @mytmp(-d) as tmp_dir {
        ...
    }


Insert External Text
--------------------

Again, in the spirit of DRY code, it may be useful to include a snippit of code
or plain text from an external source (either from a local file, an internal
network, or from the web).

.. code:: bash

    # Insert a file from the web:
    @insert https://acme.com/scripts/snippit.sh

    # Insert a gist from the web:
    @gist 5725550

    # Insert a file by relative path (and comment out each line!):
    @insert LICENSE.txt --comment


Unlike other constructs, this does not compile into some equivalent bash code.
Instead, the text is inserted directly into the document before other
constructs are evaluated. (Aliases and macros would have to be evaluated both
before and after inserting snippits).


Script Directory
----------------

The ``@dir`` alias will allow concise access to directory from which the
script is running. It is (functionally) equivalent to this:

.. code:: bash

    $(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)


Although in an attempt to make the solution *pure* bash (and not rely on
``dirname``), I think the following solution is better:

.. code:: bash

    $(cd "${BASH_SOURCE[0]%/*}" && pwd)
    # TODO: handle root


`See this Stack Overflow discussion <http://stackoverflow.com/a/246128>`_ for
the pros and cons of this approach.


Sourced
-------

The ``@sourced`` alias will allow concise checking of whether or not the
script is being sourced or called directly. It is exactly equivalent to:

.. code:: bash

    [ "${BASH_SOURCE[0]}" != "${0}" ]


It can be used to avoid side effects when the script is being sourced:

.. code:: bash

    @sourced || main "$@"


Check if Unset
--------------

The ``@notset`` macro allows for checking whether or not a variable is set
without willing it into existence. For example, ``@notset(my_var)`` is exactly
equivalent to:

.. code:: bash

    [ "_${my_var:-notset}" == "_notset" ]


Docopt
------

Docopt command-line builder:

.. code:: bash

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

    @fn main {
        @echo @args
    }

    @sourced || {
        @docopt
        main
    }


Generates something like this (untested):

.. code:: bash

    #!/bin/bash

    DOCOPT_DESC='Naval Fate.'

    DOCOPT_USAGE='
      naval_fate ship new <name>...
      naval_fate ship <name> move <x> <y> [--speed=<kn>]
      naval_fate ship shoot <x> <y>
      naval_fate mine (set|remove) <x> <y> [--moored|--drifting]
      naval_fate -h | --help
      naval_fate --version'

    DOCOPT_OPTIONS='
      -h --help     Show this screen.
      --version     Show version.
      --speed=<kn>  Speed in knots [default: 10].
      --moored      Moored (anchored) mine.
      --drifting    Drifting mine.'

    DOCOPT_VERSION='Naval Fate 2.0'

    main() {
        printf '%s\n' 'args=('
        for i in "${!args[@]}"; do
            printf '  [%q]=%q\n' "${i}" "${args[${i}]}"
        done
        printf ')\n'
    }

    docopt_usage() {
        printf 'Usage:\n%s\n\nOptions:\n%s' \
            "${DOCOPT_USAGE}" \
            "${DOCOPT_OPTIONS}"
        exit 1
    }

    docopt_help() {
        printf '%s\n\nUsage:\n%s\n\nOptions:\n%s\n\nVersion:\n  %s' \
            "${DOCOPT_DESC}" \
            "${DOCOPT_USAGE}" \
            "${DOCOPT_OPTIONS}" \
            "${DOCOPT_VERSION}"
        exit 0
    }

    docopt_version() {
        printf '%s\n' "${DOCOPT_VERSION}"
        exit 0
    }

    docopt() {
        args=()

        function docopt_error {
            printf 'Unknown option "%s"\n' "${1}"
            docopt_usage
        }

        while (( $# )); do
            if [ "${1}" == "-h" ] || [ "${1}" == "--help" ]; then
                docopt_help
            elif [ "${1}" == "--version" ]; then
                docopt_version
            elif [ "${1}" == "ship" ]; then
                shift
                if [ "${1}" == "new" ]; then
                    shift
                    if [ $# -eq 0 ]; then
                        printf 'Failed to specify at least one <name>\n'
                        docopt_usage
                    fi
                    args["<name>"]=(${@})
                    shift $#
                    args["new"]=true
                elif [ "${1}" == "shoot" ]; then
                    shift
                    if [ $# -ne 2 ]; then
                        printf 'Failed to specify arguments: <x> <y>\n'
                        docopt_usage
                    fi
                    args["<x>"]=${1}
                    args["<y>"]=${2}
                    shift 2
                    args["shoot"]=true
                else
                    if [ $# -ne 1 ]; then
                        printf 'Failed to specify argument <name>\n'
                        docopt_usage
                    fi
                    args["<name>"]=${1}
                    shift
                    if [ "${1}" == "move" ]; then
                        shift
                        if [ $# -lt 2 ]; then
                            printf 'Failed to specify arguments: <x> <y>\n'
                            docopt_usage
                        fi
                        args["<x>"]=${1}
                        args["<y>"]=${2}
                        shift 2
                        while (( $# )); do
                            if [[ "${1}" == --speed=* ]]; then
                                args["--speed"]=${1#--speed=}
                                shift
                            else
                                docopt_error "${1}"
                            fi
                        done
                        args["move"]=true
                    else
                        docopt_error "${1}"
                    fi
                fi
            elif [ "${1}" == "mine" ]; then
                shift
                if [ "${1}" == "set" ] || [ "${1}" == "remove" ]; then
                    args["${1}"]=true
                    shift
                else
                    docopt_error "${1}"
                fi
                if [ $# -lt 2 ]; then
                    printf 'Failed to specify arguments: <x> <y>\n'
                    docopt_usage
                fi
                args["<x>"]=${1}
                args["<y>"]=${2}
                shift 2
                if [ $# -eq 0 ]; then
                    :
                elif [ "${1}" == "--moored" ]; then
                    args["--moored"]=true
                    shift
                elif [ "${1}" == "--drifting" ]; then
                    args["--drifting"]=true
                    shift
                else
                    docopt_error "${1}"
                fi
                args["mine"]=true
            else
                docopt_error "${1}"
            fi
            shift
        done

        unset -f docopt_error
    }

    [ "${BASH_SOURCE[0]}" != "${0}" ] || {
        docopt "$@" 1>&2
        main
    }


Note that the above code requires Bash >= 4.0 due to the use of associative
arrays.


SSH Context
-----------

This one might be tricky to implement robustly. The idea is that the given
block of code is converted into a string and executed on the remote machine.

.. code:: bash

    @ssh user@host {
        ...
    }


The code block must be recursively inlined, then converted to a string.
