#!/bin/bash

set -e -o pipefail

readonly PACKAGE_DIR="bashup"

each_iname() {
    local iname=${1}; shift

    find * -type f -iname "${iname}" | while read -r filename; do
        "$@" "${filename}"
    done
}

static_analysis() {
    each_iname "*.rst" rst2html.py --exit-status=2 > /dev/null
    python setup.py check --strict --restructuredtext --metadata
    flake8 setup.py "${PACKAGE_DIR}"
    pyflakes setup.py "${PACKAGE_DIR}"
    pylint --reports=no --rcfile=.pylintrc "${PACKAGE_DIR}"
}

unit_test() {
    nosetests \
        --exe \
        --with-doctest \
        --doctest-options="+NORMALIZE_WHITESPACE" \
        --with-coverage \
        --cover-tests \
        --cover-inclusive \
        --cover-package="${PACKAGE_DIR}" \
        "${PACKAGE_DIR}"
}

main() {
    if [ "${1}" == "--static-analysis" ]; then
        static_analysis
    fi
    unit_test
}

if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi
