#!/bin/bash

THIS_FILE=$(readlink -f "$0")
THIS_DIR=$(dirname "$THIS_FILE")
DIR_ROOT=$(cd "$THIS_DIR"; cd ..; pwd)
LIB_VENV="${DIR_ROOT}/scripts/lib_venv.sh"
source "${LIB_VENV}"
source "${FILE_VENV}" || exit 1


function main(){
    pip3 install twine
    echo -e "Enviando ao PyPI"
    python3 -m twine upload dist/*
}


main "$@"
