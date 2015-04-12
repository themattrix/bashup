# <generated>
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

    # </generated>
    if ! grep "^tmpfs ${path}" /etc/fstab; then
        echo "tmpfs ${path} tmpfs rw,size=${size} 0 0" >> /etc/fstab
        mkdir -p "${path}"
        mount "${path}"
    fi
}
