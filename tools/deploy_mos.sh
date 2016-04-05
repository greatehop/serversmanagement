#!/bin/bash

set +x

PATH_MAIN="/home/jenkins"
PATH_DOWNLOADS_ISO="${PATH_MAIN}/sm_scripts/iso"
ARIA_OPTS="--seed-time=0 --allow-overwrite=true --force-save=true --auto-file-renaming=false --allow-piece-length-change=true"
VENV_PATH="${PATH_MAIN}/sm_scripts/venv-mos"
FUEL_QA_PATH="${PATH_MAIN}/sm_scripts/fuel-qa"

#export POOL_DEFAULT=10.177.0.0/16:24
#export NODE_VOLUME_SIZE

mkdir -p ${PATH_DOWNLOADS_ISO}

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
    echo -e "\n"
    echo "################################################################################################"
    echo "###################################  Environment Info: #########################################"
    echo "################################################################################################"
    echo -e "\n"
    dos.py net-list ${ENV_NAME}
    echo -e "\n"
    dos.py show ${ENV_NAME}

    #get random not binded port
    while true; do SSH_PORT=$(shuf -i 5000-65000 -n 1); nc ${SERVER_IP} ${SSH_PORT} < /dev/null; if [[ $? -ne 0 ]]; then break; fi done
    while true; do FUEL_PORT=$(shuf -i 5000-65000 -n 1); nc ${SERVER_IP} ${SSH_PORT} < /dev/null; if [[ $? -ne 0 ]]; then break; fi done

    echo "sshpass -p r00tme ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -f -N -L ${SERVER_IP}:${FUEL_PORT}:${FUEL_IP}:8000 root@${FUEL_IP}"
    sshpass -p r00tme ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -f -N -L ${SERVER_IP}:${FUEL_PORT}:${FUEL_IP}:8000 root@${FUEL_IP}

    echo "sshpass -p r00tme ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -f -N -L ${SERVER_IP}:${SSH_PORT}:${FUEL_IP}:22 root@${FUEL_IP}"
    sshpass -p r00tme ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -f -N -L ${SERVER_IP}:${SSH_PORT}:${FUEL_IP}:22 root@${FUEL_IP}

    echo -e "\n"
    echo "Fuel IP: ${FUEL_IP}"
    echo -e "\n"
    echo "<b>Fuel WebUI:</b> <a href='http://${SERVER_IP}:${FUEL_PORT}'>${SERVER_IP}:${FUEL_PORT}</a>"
    echo -e "\n"
    echo "<b>Fuel SSH:</b> ssh root@${SERVER_IP} -p ${SSH_PORT}"
}

ENV_NAME=${DEPLOYMENT_NAME}

source ${VENV_PATH}/bin/activate

dos.py sync

# download ISO and export ISO_PATH
get_iso "${ISO_URL}"

# build env
cd ${FUEL_QA_PATH}

./utils/jenkins/system_tests.sh -t test -w $(pwd) -j fuelweb_test -i ${ISO_PATH} -e ${ENV_NAME} -o --group=setup -V ${VENV_PATH}

dos.py start ${ENV_NAME}

# show fuel info
FUEL_ADM_IP=$(virsh net-dumpxml ${ENV_NAME}_admin | grep -oP '(\d+\.){3}' | awk '{print $0"2"}')

show_env_info "${ENV_NAME}" "${FUEL_ADM_IP}"
