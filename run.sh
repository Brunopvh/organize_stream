#!/bin/bash
#

THIS_FILE=$(readlink -f "$0")
THIS_DIR=$(dirname "$THIS_FILE")
LIB_VENV="${THIS_DIR}/scripts/lib_venv.sh"
#FILE_MAIN='organize_stream/__main__.py'
FILE_MAIN='teste.py'
source "$LIB_VENV" || exit 1
source "$FILE_VENV" || exit 1
	

function main() {
  clear
  echo -e "VENV [$FILE_VENV]"
  python "${THIS_DIR}/${FILE_MAIN}"
}

main "$@"
