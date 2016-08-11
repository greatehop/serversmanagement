#!/bin/bash

set +x

PATH_MAIN=$(pwd)
VENV_PATH="${PATH_MAIN}/sm_scripts/${VENV}"

source ${VENV_PATH}/bin/activate

dos.py sync

dos.py erase ${DEPLOYMENT_NAME}