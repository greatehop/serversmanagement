#!/bin/bash

set +x

PATH_MAIN="/home/jenkins"
VENV_PATH="${PATH_MAIN}/scripts/venv-mos"

source ${VENV_PATH}/bin/activate

dos.py sync

dos.py erase ${DEPLOYMENT_NAME}