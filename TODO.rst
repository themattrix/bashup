Planned Constructs
==================

Context Managers
----------------

  Inspired by `Python's  @contextmanager decorator <https://docs.python.org/3.4/library/contextlib.html#contextlib.contextmanager>`_.

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
    @with(mktemp -d) as tmp ...


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


Note that the body of the context ends up being evaluated in a subshell.


Aliases
-------

Aliases would be useful for keeping your bashup code as `DRY <http://en.wikipedia.org/wiki/Don%27t_repeat_yourself>`_ as possible. They'd have to be evaluated before any other
constructs.

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
