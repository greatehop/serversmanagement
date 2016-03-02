from fabric.api import env, run, prefix
from fabric.context_managers import shell_env

#env.roledefs = {
#    'dev': ['jenkins@172.18.196.233']
#}

#TODO: add deploy_mos script
def install_tasks():
    pass

def deploy_mos():
    """
    with shell_env(DEPLOYMENT_NAME='test_fabric', ISO_PATH='/home/jenkins/scripts/iso/fuel-8.0-529-2016-02-05_13-56-13.iso'):
        run('/home/jenkins/scripts/deploy_mos.sh')
    """
    #run('export LANG=en_EN; for i in {1..5}; do  ls -l /opt ; sleep 10; done')
    run('uptime')
        
def clean_mos():
    pass