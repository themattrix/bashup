Planned Constructs
==================

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

    function with_mktemp() {(
        local body_fn=${1}; shift
        local tmp=$(mktemp "$@")

        function exit_ctx() {
            rm -f "${tmp}"
        }

        trap exit_ctx EXIT

        "${body_fn}" "${tmp}"
    )}

    ...

    function ctx_0() {
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
        set +e +o pipefail
        "$@" || true
        set -e -o pipefail
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

    function ignore_failure {
        set +e +o pipefail
        "$@" || true
        set -e -o pipefail
    }

    function show_args {
        echo ">>> $@"
        "$@"
    }

    function enable_ramdisk {
        ...
    }

    eval "$(echo "enable_ramdisk() {"; )"

    function enable_ramdisk_0 {
        show_args enable_ramdisk_orig "$@"
    }


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

    @{mytmp} = @with(mktemp tmp.XXXXXXXXXXXXXXXXXXXXXXXXXX)


The alias can then be treated as a literal text substitution:

.. code:: bash

    @{mytmp} as tmp {
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
    @insert --comment LICENSE.txt


Unlike other constructs, this does not compile into some equivalent bash code.
Instead, the text is inserted directly into the document before other
constructs are evaluated. (Aliases would have to be evaluated both before and
after inserting snippits).


Script Directory
----------------

The ``@{dir}`` alias will allow concise access to directory from which the
script is running. It is (functionally) equivalent to this:

.. code:: bash

    $(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)


Although in an attempt to make the solution *pure* bash (and not rely on
``dirname``), I think the following solution is better:

.. code:: bash

    $(cd "${BASH_SOURCE[0]%/*}" && pwd)


`See this Stack Overflow discussion <http://stackoverflow.com/a/246128>`_ for
the pros and cons of this approach.


Sourced
-------

The ``@{sourced}`` alias will allow concise checking of whether or not the
script is being sourced or called directly. It is exactly equivalent to:

.. code:: bash

    [ "${BASH_SOURCE[0]}" != "${0}" ]


It can be used to avoid side effects when the script is being sourced:

.. code:: bash

    @{sourced} || main "$@"


Check if Unset
--------------

The ``@{notset}`` alias allows for checking whether or not a variable is set
without willing it into existence. For example, ``@{notset my_var}`` is exactly
equivalent to:

.. code:: bash

    [ "_${my_var:-notset}" == "_notset" ]


Include Guard
-------------

The include guard will be auto-added...?

.. code:: bash

    if [ -z "${INCLUDE_GUARD_16FD270}" ]; then
    readonly INCLUDE_GUARD_16FD270=1

    ...

    fi

    @{sourced} || main "$@"


Anonymous Functions
-------------------

.. code:: bash

    @fn cpuinfo {
        "${1}" < /proc/cpuinfo
    }

    cpuinfo @[grep '^processor']


I'd prefer a syntax with curly braces (``@{...}``), but aliases already has
claim to them.


SSH Context
-----------

This one might be tricky to implement robustly. The idea is that the given
block of code is converted into a string and executed on the remote machine.

.. code:: bash

    @ssh user@host {
        ...
    }


The code block must be recursively inlined, then converted to a string.
