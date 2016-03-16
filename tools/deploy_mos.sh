#!/bin/bash

set +x

PATH_MAIN="/home/jenkins"
PATH_DOWNLOADS_ISO="${PATH_MAIN}/scripts/iso"
ARIA_OPTS="--seed-time=0 --allow-overwrite=true --force-save=true --auto-file-renaming=false  --allow-piece-length-change=true"
VENV_PATH="${PATH_MAIN}/scripts/venv-mos"
FUEL_QA_PATH="${PATH_MAIN}/scripts/fuel-qa"

function get_iso() {
    ISO_URL="$1"
    ISO_FILE=${ISO_URL##*/}
    ISO_FILE=${ISO_FILE%.torrent}

    aria2c -d ${PATH_DOWNLOADS_ISO} ${ARIA_OPTS} ${ISO_URL}
    ISO_PATH="${PATH_DOWNLOADS_ISO}/${ISO_FILE}"
}

function show_env_info() {
    ENV_NAME="$1"
    FUEL_IP="$2"
    set +x
    echo "################################################################################################"
    echo "###################################  Environment Info: #########################################"
    echo "################################################################################################"
    echo -e "\n"
    echo "Fuel IP: http://${FUEL_IP}:8000"
    echo -e "\n"
    dos.py net-list ${ENV_NAME}
    echo -e "\n"
    dos.py show ${ENV_NAME}
    echo -e "\n"
}

ENV_NAME=${DEPLOYMENT_NAME}

source ${VENV_PATH}/bin/activate

dos.py sync

# download ISO and export ISO_PATH
get_iso "${ISO_URL}"

# build env
cd ${FUEL_QA_PATH}

./utils/jenkins/system_tests.sh -t test -w $(pwd) -j fuelweb_test -i ${ISO_PATH}  -e ${ENV_NAME} -o --group=setup -V ${VENV_PATH}

dos.py start ${ENV_NAME}

# show fuel info
FUEL_ADM_IP=$(virsh net-dumpxml ${ENV_NAME}_admin | grep -P "(\d+\.){3}" -o | awk '{print ""$0"2"}')

show_env_info "${ENV_NAME}" "${FUEL_ADM_IP}"
