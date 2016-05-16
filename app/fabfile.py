from fabric.api import env, run, task, put
from fabric.context_managers import shell_env

env.output_prefix = False


@task
def verify_ssh():
    run('uptime')


@task
def deploy_mos(**kwargs):
    """Task "deploy_mos" for deploy Fuel node"""
    put('tools/deploy_mos.sh', '~/sm_scripts/', mode=0755)
    with shell_env(SLAVE_NODE_MEMORY=kwargs['slave_node_memory'],
                   SLAVE_NODE_CPU=kwargs['slave_node_cpu'],
                   NODES_COUNT=kwargs['nodes_count'],
                   DEPLOYMENT_NAME=kwargs['deploy_name'],
                   ISO_URL=kwargs['iso_url'],
                   SERVER_IP=kwargs['server_ip'],
                   VENV=kwargs['venv']):
        run('~/sm_scripts/deploy_mos.sh')


@task
def clean_mos(**kwargs):
    """Task "clean_mos" for clean up Fuel node"""
    put('tools/clean_mos.sh', '~/sm_scripts/', mode=0755)
    with shell_env(DEPLOYMENT_NAME=kwargs['deploy_name'],
                   VENV=kwargs.get('venv', 'venv-mos')):
        run('~/sm_scripts/clean_mos.sh')
