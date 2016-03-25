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
                   NODES_COUNT=kwargs['nodes_count']):
        run('/var/lib/jenkins/scripts/deploy_mos.sh')

@task
def clean_mos(**kwargs):
    """
    Task "clean_mos" for clean up Fuel node
    """

    with shell_env(DEPLOYMENT_NAME=kwargs['deploy_name']):
        run('/var/lib/jenkins/scripts/clean_mos.sh')