#!/bin/bash

THIS_FILE=$(readlink -f "$0")
THIS_DIR=$(dirname "$THIS_FILE")
DIR_ROOT=$(cd "$THIS_DIR"; cd ..; pwd)
LIB_VENV="${DIR_ROOT}/scripts/lib_venv.sh"
source "${LIB_VENV}"
source "${FILE_VENV}" || exit 1

function main(){
    pip3 install build
    python3 -m build

    echo -e "\n"
    echo "Use: python3 -m twine upload dist/*"
    echo "Para enviar ao PyPI"
}


main "$@"
