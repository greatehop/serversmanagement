import settings
from app import models, db, socketio

from subprocess import Popen, PIPE
from threading import Thread
from time import sleep
import random
import datetime
from flask.ext.socketio import SocketIO, emit

class ReadWriteStream(object):
    """
    console output reader/writer
    """

    def __init__(self, stream, run_id):
        self.stream = stream
        self.data = []

        def rw_output(stream, data):
            while True:
                line = stream.readline()
                if line:
                    # send line to client
                    socketio.emit('line', {'data': line }, namespace='/test')

                    data.append(line)
                else:
                    # "convert" console nextline (\n) to html nextline (<br>)
                    cmd_out = '<br>'.join([i for i in data])
                    # update run - set cmd_out, run_state and end_datetime
                    run_state = settings.RUN_STATE['done']
                    end_datetime = datetime.datetime.utcnow()
                    db.session.query(models.Run).filter_by(id=run_id).update(
                        {'state': run_state,
                         'end_datetime': end_datetime,
                         'cmd_out': cmd_out})
                    db.session.commit()
                    break

        self.t = Thread(target=rw_output, args =(self.stream, self.data))
        self.t.daemon = True
        self.t.start()

class Scheduler(object):
    """
    daemon for execute runs in queue
    """

    #TODO: add interupt handler
    #TODO: add delete env by keep days argument
    def __init__(self):
        def daemon():
            state_inq = settings.RUN_STATE['in_queue']
            while True:
                runs_in_queue = models.Run.query.order_by(
                    models.Run.id).filter_by(state=state_inq, task_id=1).all()

                if runs_in_queue:
                    print runs_in_queue
                    for run in runs_in_queue:
                        # get server and execute run
                        server = get_server()
                        print server
                        if server:
                            task = models.Task.query.get(run.task_id)
                            run_task(task, server, run)
                        else:
                            break

                sleep(settings.DAEMON_TIMEOUT)

        main = Thread(target=daemon)
        main.daemon = True
        main.start()

def get_server():
    """
    get random and not loaded server (based on max/cur tasks in db) or None
    and update server state
    """

    #TODO: add lock
    server_state = settings.SERVER_STATE['on']
    server_list = models.Server.query.filter_by(state=server_state).all()
    tmp_list = [{'id': s, 'weight': s.max_tasks-s.cur_tasks}
                for s in server_list if s.max_tasks-s.cur_tasks]
    random.shuffle(tmp_list)
    try:
        server = max(tmp_list, key=lambda i: i['weight'])['id']
        # increase current number of tasks
        db.session.query(models.Server).filter_by(id=server.id).update(
            {'cur_tasks': models.Server.cur_tasks+1})
        db.session.commit()
        return server
    except ValueError:
        return None

def run_task(task, server, run):
    """
    execute task (fabric file) and save console output in background

    example: 
    fab --fabfile <fabfile> -u <user> 
        -H <ip> <taskname>[:key1=val1,keyN=valN]
    """

    # update run - set "in_progress" and "server_id"
    run_state = settings.RUN_STATE['in_progress']
    db.session.query(models.Run).filter_by(id=run.id).update(
        {'state': run_state, 'server_id': server.id})
    db.session.commit()

    #TODO: use fabric API?
    cmd = 'fab --fabfile=%s -u %s -H %s %s' % (
        task.taskfile, settings.SSH_USER, server.ip, task.taskname)

    # add arguments for task
    if run.args:
        vars = ','.join(['%s="%s"' % (key, val)
                         for key, val in run.args.iteritems()])
        cmd += ':%s' % vars

    # run command and write output to web/db in background
    process = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
    ReadWriteStream(process.stdout, run.id)

    #TODO: add cancel
    return process