#!/usr/bin/env bash

mkdir -p ~/sm_scripts/iso

# current release
cd ~/sm_scripts/
virtualenv --no-site-packages venv-mos
git clone http://github.com/openstack/fuel-qa ./venv-mos/fuel-qa
source ./venv-mos/bin/activate
cd ./venv-mos/fuel-qa/
pip install -r ./fuelweb_test/requirements.txt --upgrade
deactivate

# old releases
for VER in "6.1" "7.0" "8.0"
do
  cd ~/sm_scripts/
  virtualenv --no-site-packages venv-mos${VER}
  git clone -b stable/${VER} http://github.com/openstack/fuel-qa ./venv-mos${VER}/fuel-qa
  source ./venv-mos${VER}/bin/activate
  cd ./venv-mos${VER}/fuel-qa/
  pip install -r ./fuelweb_test/requirements.txt --upgrade
  deactivate
done
