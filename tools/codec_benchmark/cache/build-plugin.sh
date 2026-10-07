#!/bin/sh
set -eu
if [ "$#" -ne 2 ]; then
    echo "Usage: sh build-plugin.sh /path/to/qemu-source /path/to/output-directory" >&2
    exit 2
fi
source_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
mkdir -p "$2"
cc -O3 -std=c11 -Wall -Wextra -Werror -fPIC -shared -fvisibility=hidden \
    -I"$1/include/qemu" $(pkg-config --cflags glib-2.0) \
    "$source_dir/esp32c3_cache.c" -o "$2/esp32c3_cache.so"
cc -O2 -std=c11 -Wall -Wextra -Werror \
    "$source_dir/../../../tests/test-esp32c3-cache-model.c" -o "$2/test-cache-model"
"$2/test-cache-model"
