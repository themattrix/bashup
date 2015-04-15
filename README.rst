Bashup |Version| |Build| |Coverage| |Health|
============================================

|Compatibility| |Implementations| |Format| |Downloads|

A (toy) language that compiles to bash.

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

        for ((i = 1; i < $#; i++)); do
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
