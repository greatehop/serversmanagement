from fabric import api as fab_api
from fabric import context_managers as fab_cm

fab_api.env.output_prefix = False


@fab_api.task
def verify_ssh():
    fab_api.run('uptime')


@fab_api.task
def deploy_mos(**kwargs):
    """Task "deploy_mos" for deploy Fuel node"""
    fab_api.put('tools/deploy_mos.sh', '~/sm_scripts/', mode=0o755)
    with fab_cm.shell_env(SLAVE_NODE_MEMORY=kwargs['slave_node_memory'],
                          SLAVE_NODE_CPU=kwargs['slave_node_cpu'],
                          NODES_COUNT=kwargs['nodes_count'],
                          DEPLOYMENT_NAME=kwargs['deploy_name'],
                          ISO_URL=kwargs['iso_url'],
                          IRONIC_NODES_COUNT=kwargs['ironic_nodes_count'],
                          IRONIC_ENABLED=kwargs['ironic_enabled'],
                          SERVER_IP=kwargs['server_ip'],
                          VENV=kwargs['venv']):
        fab_api.run('~/sm_scripts/deploy_mos.sh')


@fab_api.task
def clean_mos(**kwargs):
    """Task "clean_mos" for clean up Fuel node"""
    fab_api.put('tools/clean_mos.sh', '~/sm_scripts/', mode=0o755)
    with fab_cm.shell_env(DEPLOYMENT_NAME=kwargs['deploy_name'],
                          VENV=kwargs.get('venv', 'venv-mos')):
        fab_api.run('~/sm_scripts/clean_mos.sh')
