#!/bin/bash

set +x

PATH_MAIN="/home/jenkins"
PATH_DOWNLOADS_ISO="${PATH_MAIN}/sm_scripts/iso"
ARIA_OPTS="--seed-time=0 --allow-overwrite=true --force-save=true --auto-file-renaming=false --allow-piece-length-change=true --show-console-readout=true"
VENV_PATH="${PATH_MAIN}/sm_scripts/${VENV}"
FUEL_QA_PATH="${PATH_MAIN}/sm_scripts/${VENV}/fuel-qa"

mkdir -p ${PATH_DOWNLOADS_ISO}

function get_iso() {
    echo -e "Downloading ISO...\n"
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
    echo -e "\n"

    #get random not binded port
    while true; do SSH_PORT=$(shuf -i 5000-65000 -n 1); nc ${SERVER_IP} ${SSH_PORT} < /dev/null; if [[ $? -ne 0 ]]; then break; fi done
    while true; do FUEL_PORT=$(shuf -i 5000-65000 -n 1); nc ${SERVER_IP} ${SSH_PORT} < /dev/null; if [[ $? -ne 0 ]]; then break; fi done

    echo "sshpass -p r00tme ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -f -N -L ${SERVER_IP}:${FUEL_PORT}:${FUEL_IP}:8000 root@${FUEL_IP}"
    sshpass -p r00tme ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -f -N -L ${SERVER_IP}:${FUEL_PORT}:${FUEL_IP}:8000 root@${FUEL_IP}

    echo "sshpass -p r00tme ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -f -N -L ${SERVER_IP}:${SSH_PORT}:${FUEL_IP}:22 root@${FUEL_IP}"
    sshpass -p r00tme ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -f -N -L ${SERVER_IP}:${SSH_PORT}:${FUEL_IP}:22 root@${FUEL_IP}

    if [[ "$?" -eq 0 ]]; then
        echo -e "map between kvm nodes and fuel nodes (id, ip, kvm_name)\n"
        sshpass -p r00tme ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@${FUEL_IP} "fuel node | awk '/^[0-9]/{print}' | tr -d '()'" > /tmp/fuel_node.txt
        for i in $(virsh list| grep "${ENV_NAME}" | awk '{print $2}'); do awk -v mac=$(virsh dumpxml ${i}| grep -oP "admin_\K(\w{2}:?){6}") -v i=$i '{if (mac ~ $6) print $1, $10, i}' /tmp/fuel_node.txt; done

        if ${IRONIC_ENABLED}; then
            echo -e "Ironic node(s) MAC\n"
            for i in $(virsh list --all| grep "${ENV_NAME}_ironic" | awk '{print $2}'); do echo ${i}; virsh dumpxml ${i} | grep -oP "mac address='\K[^']+"; done
        fi

        echo -e "\n"
        echo "Server IP: ${SERVER_IP}"
        echo -e "\n"
        echo "Fuel IP: ${FUEL_IP}"
        echo -e "\n"
        echo "<b>Fuel WebUI:</b> <a href='http://${SERVER_IP}:${FUEL_PORT}'>${SERVER_IP}:${FUEL_PORT}</a>"
        echo -e "\nuser/pass: admin/admin\n"
        echo "<b>Fuel SSH:</b> ssh root@${SERVER_IP} -p ${SSH_PORT}"
        echo -e "\nuser/pass: root/r00tme\n"
    else
        echo "<b>Something has gone wrong! Connect to server (ssh ${SERVER_IP}) and try to debug.</b>"
    fi
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

# wait while nodes are booted
sleep 60

# show fuel info
FUEL_ADM_IP=$(virsh net-dumpxml ${ENV_NAME}_admin | grep -oP '(\d+\.){3}' | awk '{print $0"2"}')

show_env_info "${ENV_NAME}" "${FUEL_ADM_IP}"
