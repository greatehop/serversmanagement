import logging
import logging.config
import operator
import threading

import pyzabbix

from serversmanagement.app.database import models
from serversmanagement import settings

logger = logging.getLogger(__name__)

_lock = threading.Lock()
_zabbix = pyzabbix.ZabbixAPI(settings.ZABBIX_LINK)
_zabbix.login(user="guest")

logger.info("Connected to Zabbix API. Version {0}.".format(
    _zabbix.api_version()))


class HostNotFoundException(Exception):
    pass


def get_zabbix_server_by_name(server_name):
    zabbix_server = _zabbix.host.get(filter={"host": server_name})
    if zabbix_server:
        logger.debug("Server with name '{name} was found in zabbix.'".format(
            name=server_name
        ))
        return zabbix_server[0]

    raise HostNotFoundException(
        "Server with name '{0} can't be found in zabbix.'".format(server_name)
    )


def get_server_total_ram_mb(zabbix_server):
    server_free_ram = _zabbix.item.get(
        filter={"name": "Total memory",
                "hostid": zabbix_server['hostid']},
        application="Memory")[0]
    return int(server_free_ram['lastvalue']) / (1024 * 1024)


def get_server_total_space_gb(zabbix_server):
    server_free_space = _zabbix.item.get(
        filter={"name": "Total disk space on $1",
                "key_": "vfs.fs.size[/,total]",
                "hostid": zabbix_server['hostid']},
        application="Filesystems")[0]
    return int(server_free_space['lastvalue']) / (1024 * 1024 * 1024)


def reserve_server(run):
    """Get the least powerful server which have enough CPU and RAM"""

    logger.debug("Reserve server function")
    with _lock:
        server_filter = {'state': settings.SERVER_STATE['on']}
        server_list = models.Server.query.filter_by(**server_filter).all()
        possible_servers = []
        required_ram = run.args['slave_node_memory'] * run.args['nodes_count']
        # TODO(calc using params):
        required_disk = 100

        for server in server_list:
            try:
                zabbix_server = get_zabbix_server_by_name(server.alias)
            except HostNotFoundException as exc:
                logger.warn(exc.message)
            else:
                total_ram = get_server_total_ram_mb(zabbix_server)
                free_ram = total_ram - server.used_ram

                total_disk = get_server_total_space_gb(zabbix_server)
                free_disk = total_disk - server.used_disk

                system_ram = settings.RESERVED_BY_SYSTEM_RAM
                system_disk = settings.RESERVED_BY_SYSTEM_DISK

                if (free_ram - required_ram > system_ram and
                        free_disk - required_disk > system_disk):
                    possible_servers.append(
                        (server, server.cur_tasks, free_ram, free_disk))

        if possible_servers:
            server = min(possible_servers, key=operator.itemgetter(1, 2, 3))[0]
            server.add_env_to_server(run)

            return server
