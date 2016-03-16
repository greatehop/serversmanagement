from fabric.api import env, run, prefix, task
from fabric.context_managers import shell_env

env.output_prefix = False

@task
def verify_ssh():
    run('uptime')

@task
def deploy_mos(**kwargs):
    """
    Task "deploy_mos" for deploy Fuel node
    """

    with shell_env(ISO_URL=kwargs['iso_url'],
                   KEEP_DAYS=kwargs['keep_days'],
                   DEPLOYMENT_NAME=kwargs['deploy_name'],
                   SLAVE_NODE_MEM=kwargs['slave_node_mem'],
                   SLAVE_NODE_CPU=kwargs['slave_node_cpu'],
                   NODE_COUNT=kwargs['node_count']):
        run('/var/lib/jenkins/scripts/deploy_mos.sh')

    # for tests
    #run('for i in {1..20}; do echo ${i}; uptime; sleep 2; done')

@task
def clean_mos(**kwargs):
    """
    Task "clean_mos" for clean up Fuel node
    """

    with shell_env(DEPLOY_NAME=kwargs['deploy_name']):
        run('VENV_PATH="/home/jenkins/scripts/venv-mos"')
        run('source ${VENV_PATH}/bin/activate')
        run('dos.py sync')
        run('ENV_NAME=${DEPLOY_NAME}')
        run('dos.py erase ${ENV_NAME}')

        # for tests
        #run('echo ${DEPLOY_NAME}')