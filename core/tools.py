from Queue import Queue, Empty
from subprocess import Popen, PIPE
from threading import Thread
from time import sleep
import random

import config
from app import models, db

#TODO: fix it!
class NonBlockingStreamReader:

    def __init__(self, stream):
        self._s = stream
        self._q = Queue()

        def _populateQueue(stream, queue):
            while True:
                line = stream.readline()
                if line:
                    queue.put(line)

        self._t = Thread(target = _populateQueue, args = (self._s, self._q))
        self._t.daemon = True
        self._t.start()

    def readline(self, timeout = None):
        try:
            return self._q.get(block = timeout is not None, timeout = timeout)
        except Empty:
            return None

def get_server():
    """
    random get not loaded and not disabled server or None
    """
    #TODO: get env_per_server variable

    server_list = models.Server.query.filter_by(state=config.SERVER_STATE['on']).all()
    if server_list:
        return random.choice(server_list)
    return None

def run_task(task_name, task_file, task_server):
    #TODO: use fabric API?
    #TODO: add task cancel (--abort-on-prompts=True)
    
    #example: fab deploy_mos --fabfile ./fabfile.py --host 172.18.196.233 -u jenkins
    cmd = 'fab %s --fabfile=%s -u %s -H %s' % (task_name, task_file, config.SSH_USER, task_server)
    p = Popen(cmd, stdin = PIPE, stdout = PIPE, stderr = PIPE, shell = True)
    #TODO: save pid
    #+ output http://docs.fabfile.org/en/latest/usage/output_controls.html
    
    #TODO: update run state
    nbsr = NonBlockingStreamReader(p.stdout)
  
    #TODO: fix timeout
    cmd_out = nbsr.readline(1)
    #print cmd_out
    return cmd_out

#TODO: need daemon
def scheduler():
    """
    get run_id fitered by lower id
    """ 
    #TODO: delete env by keep_days parameter
    runs_in_queue = models.Run.query.filter_by(config.RUN_STATE['in_queue'])
    
    time.sleep(config.SCHEDULER_TIMEOUT)
    pass
     