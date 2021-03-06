#!/bin/bash

if [ -n "$DEBUG" ]; then
    PS4=':${LINENO}+'
    set -x
fi

REAL_FILE="$0"
REAL_NAME="$(basename "$REAL_FILE")"
REAL_PATH="$(dirname "$REAL_FILE")"
if [ -L "$0" ]; then
    LINK_FILE=$REAL_FILE; REAL_FILE="$(readlink "$0")"
    LINK_NAME=$REAL_NAME; REAL_NAME="$(basename "$REAL_FILE")"
    LINK_PATH=$REAL_PATH; REAL_PATH="$(dirname "$REAL_FILE")"
fi

function mawsh() {
    . $REAL_PATH/bin/mawsh
    _mawsh_main "$@"
}
