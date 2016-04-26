#!/bin/bash

set +x

VENV_PATH="~/sm_scripts/venv-mos"

source ${VENV_PATH}/bin/activate

dos.py sync

dos.py erase ${DEPLOYMENT_NAME}