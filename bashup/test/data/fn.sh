#!/bin/bash

set -e -o pipefail

#
# usage: enable_ramdisk --size=<SIZE> [--path=<PATH>] [ARGS]
#
enable_ramdisk() {
    local size
    local size__set=0
    local path='/ramdisk'
    local args=()

    while (( $# )); do
        if [[ "${1}" == --size=* ]]; then
            size=${1#--size=}
            size__set=1
        elif [[ "${1}" == --path=* ]]; then
            path=${1#--path=}
        else
            args+=("${1}")
        fi
        shift
    done

    if ! (( size__set )); then
        echo "[ERROR] The --size parameter must be given."
        return 1
    fi

    __enable_ramdisk "${size}" "${path}" "${args[@]}"
}

__enable_ramdisk() {
    local size=${1}
    local path=${2}
    shift 2

    if ! grep "^tmpfs ${path}" /etc/fstab; then
        echo "tmpfs ${path} tmpfs rw,size=${size} 0 0" >> /etc/fstab
        mkdir -p "${path}"
        mount "${path}"
    fi
}

#
# usage: ensure_root [ARGS]
#
ensure_root() {
    if [ ${EUID} -ne 0 ]; then
        echo "[ERROR] Script must be run as root."
        return 1
    fi
}

ensure_root
enable_ramdisk --size="4G"
