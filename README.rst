Bashup |Version| |Build| |Coverage| |Health|
============================================

|Compatibility| |Implementations| |Format| |Downloads|

A (toy) language that compiles to bash.
You can think of bashup as just a little syntactic sugar sprinkled on top of bash;
any valid bash script is also a valid bashup script.

  *Just a spoonful of sugar makes the bashisms go down...*


.. code:: bash

    #/bin/bash

    @fn hi greeting='Hello', target {
        echo "${greeting}, ${target}!"
    }

    hi --target 'World'


Installation:

.. code:: shell

    $ pip install bashup


Compile and run the above example:

.. code:: shell

    $ bashup -i above_example.bashup -o above_example.sh
    $ bash above_example.sh
    Hello, World!


Or just run it directly:

.. code:: shell

    $ bashup -r above_example.bashup
    Hello, World!


Compiled code (``above_example.sh``):

.. code:: bash

    #/bin/bash

    #
    # usage: hi [--greeting <GREETING>] --target <TARGET> [ARGS]
    #
    function hi() {
        local greeting='Hello'
        local target
        local target__set=0
        local args=()
        local i

        for ((i = 1; i <= $#; i++)); do
            if [ "${!i}" == "--greeting" ]; then
                ((i++))
                greeting=${!i}
            elif [ "${!i}" == "--target" ]; then
                ((i++))
                target=${!i}
                target__set=1
            else
                args+=("${!i}")
            fi
        done

        if [ ${target__set} -eq 0 ]; then
            echo "[ERROR] The --target parameter must be given."
            return 1
        fi

        __hi "${greeting}" "${target}" "${args[@]}"
    }

    function __hi() {
        local greeting=${1}
        local target=${2}
        shift 2

        echo "${greeting}, ${target}!"
    }

    hi --target 'World'


Supported Bash Versions
-----------------------

The generated bash code works with bash 3.1 and above (tested against 3.1 to 4.3).


Nifty Features
--------------

Bashup tries its best to match the indentation of its compiled code against your hand-written bash.
For example:

.. code:: bash

    @fn hi greeting='Hello', target {
      echo "${greeting}, ${target}!"
    }

...compiles to:

.. code:: bash

    #
    # usage: hi [--greeting <GREETING>] --target <TARGET> [ARGS]
    #
    function hi() {
      local greeting='Hello'
      local target
      local target__set=0
      local args=()
      local i

      for ((i = 1; i <= $#; i++)); do
        if [ "${!i}" == "--greeting" ]; then
          ((i++))
          greeting=${!i}
          ...


Changelog
---------

**1.1.1**

- Tweaked the README.


**1.1.0**

- Fixed - |Issue2|__
- Feature - |Issue3|__
- Fixed - |Issue4|__


**1.0.0**

- Initial release, supports ``@fn`` syntax.


.. Badges

.. |Build| image:: https://travis-ci.org/themattrix/bashup.svg?branch=master
   :target: https://travis-ci.org/themattrix/bashup
.. |Coverage| image:: https://img.shields.io/coveralls/themattrix/bashup.svg
   :target: https://coveralls.io/r/themattrix/bashup
.. |Health| image:: https://landscape.io/github/themattrix/bashup/master/landscape.svg
   :target: https://landscape.io/github/themattrix/bashup/master
.. |Version| image:: https://pypip.in/version/bashup/badge.svg?text=version
   :target: https://pypi.python.org/pypi/bashup
.. |Downloads| image:: https://pypip.in/download/bashup/badge.svg
   :target: https://pypi.python.org/pypi/bashup
.. |Compatibility| image:: https://pypip.in/py_versions/bashup/badge.svg
   :target: https://pypi.python.org/pypi/bashup
.. |Implementations| image:: https://pypip.in/implementation/bashup/badge.svg
   :target: https://pypi.python.org/pypi/bashup
.. |Format| image:: https://pypip.in/format/bashup/badge.svg
   :target: https://pypi.python.org/pypi/bashup


.. Issues

.. |Issue2| replace:: Issue #2: "Run generated bash code against multiple versions of bash."
__ https://github.com/themattrix/bashup/issues/2

.. |Issue3| replace:: Issue #3: "Allow running of bashup scripts directly."
__ https://github.com/themattrix/bashup/issues/3

.. |Issue4| replace:: Issue #4: "Last positional parameter to @fn may not be passed to generated function."
__ https://github.com/themattrix/bashup/issues/4
