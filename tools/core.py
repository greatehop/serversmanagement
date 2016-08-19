import settings
from app.database import models
from app.extensions import db, socketio

import os
import signal
from subprocess import Popen, PIPE
from threading import Thread, Lock
from datetime import datetime
import random
from time import sleep


lock = Lock()


class ReadWriteStream(object):
    """console output reader/writer"""

    def __init__(self, stream, run_id):
        self.stream = stream
        self.data = []

        @socketio.on('connect', namespace='/run%s' % run_id)
        def on_connect():
            for line in self.data:
                socketio.emit('line', {'data': line},
                              namespace='/run%s' % run_id)

        def rw_output(stream, data):
            while True:
                line = stream.readline()
                if line:
                    # send line to client
                    socketio.emit('line', {'data': line},
                                  namespace='/run%s' % run_id)

                    data.append(line)
                else:
                    # "convert" console nextline (\n) to html nextline (<br>)
                    cmd_out = '<br>'.join([i for i in data])

                    # update run - set cmd_out, run_state and end_datetime
                    run_state = settings.RUN_STATE['done']
                    end_datetime = datetime.utcnow()
                    db.session.query(models.Run).filter_by(id=run_id).update(
                        {'state': run_state,
                         'end_datetime': end_datetime,
                         'cmd_out': cmd_out})
                    db.session.commit()

                    # send "singnal" for force page update
                    socketio.emit('stop', namespace='/run%s' % run_id)
                    socketio.emit('stop', namespace='/runs')
                    break

        self.t = Thread(target=rw_output, args=(self.stream, self.data))
        self.t.daemon = True
        self.t.start()


class Scheduler(Thread):
    """daemon for execute runs in queue"""

    def __init__(self):
        Thread.__init__(self)
        self.daemon = True

    def run(self):
        while True:
            filter = {'state': settings.RUN_STATE['in_queue'], 'task_id': 1}
            runs_in_queue = models.Run.query.order_by(
                models.Run.id).filter_by(**filter).all()
            if runs_in_queue:
                for run in runs_in_queue:
                    # get server and execute run
                    server = get_server()
                    if server:
                        task = models.Task.query.get(run.task_id)
                        run_task(task, server, run)
                    else:
                        break

            """
            # delete old envs (based on keep_days argument)
            filter2 = {'state': settings.RUN_STATE['done'], 'task_id': 1}
            runs_for_del = models.Run.query.order_by(
                models.Run.id).filter_by(**filter2).all()

            for run in runs_for_del:
                keep_days = int(run.args['keep_days'])
                if keep_days:
                    cur_time = datetime.utcnow()
                    judgment_day = run.end_datetime + timedelta(
                        minutes=keep_days)
                    if cur_time >= judgment_day:
                        # execute run
                        task = models.Task.query.get(2)
                        server = models.Server.query.get(run.server_id)
                        run_task(task, server, run)

                        # mark existing run as removed
                        db.session.query(models.Run).filter_by(
                            id=run.id).update(
                            {'state': settings.RUN_STATE['removed']})
                        db.session.commit()

                        # decrease current number of tasks
                        update_server({'id': run.server_id}, add=False)
            """

            # forse close transaction
            db.session.commit()

            sleep(settings.DAEMON_TIMEOUT)


def get_server():
    """get random and not loaded server
    (based on max/cur tasks in db) or None
    """

    with lock:
        filter = {'state': settings.SERVER_STATE['on']}
        server_list = models.Server.query.filter_by(**filter).all()
        tmp_list = [{'id': s, 'weight': int(s.max_tasks) - int(s.cur_tasks)}
                    for s in server_list if int(s.max_tasks)-int(s.cur_tasks)]
        random.shuffle(tmp_list)
        try:
            server = max(tmp_list, key=lambda i: i['weight'])['id']
            # increase current number of tasks
            update_server({'id': server.id})
            return server
        except ValueError:
            return None


def run_task(task, server, run):
    """execute task (fabric file) and save console output in background

    example:
    fab --fabfile <fabfile> -u <user>
        -H <ip> <taskname>[:key1=val1,keyN=valN]
    """

    cmd = 'fab --fabfile=%s -u %s -H %s %s' % (
        task.taskfile, settings.SSH_USER, server.ip, task.taskname)

    # add arguments for task
    if run.args:
        vars = ','.join(['%s="%s"' % (key, val)
                         for key, val in run.args.iteritems()])
        vars += ',server_ip=%s' % server.ip
        cmd += ':%s' % vars

    # run command and write output to web/db in background
    process = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE,
                    shell=True, preexec_fn=os.setsid)
    pid = process.pid
    ReadWriteStream(process.stdout, run.id)

    # update run info
    run_state = settings.RUN_STATE['in_progress']
    args = run.args
    args.update({'pid': pid})
    db.session.query(models.Run).filter_by(id=run.id).update(
        {'state': run_state, 'server_id': server.id, 'args': args})
    db.session.commit()


# TODO(hop): move to models???
def update_server(filter, add=True):
    """increase/decrease current number of tasks"""
    val = 1
    if not add:
        val = -1
    db.session.query(models.Server).filter_by(**filter).update(
        {'cur_tasks': models.Server.cur_tasks + val})
    db.session.commit()


def kill(pid):
    try:
        os.killpg(os.getpgid(pid), signal.SIGTERM)
        # TODO(hop): update state: 'canceled', decrease server number
    except Exception:
        pass


def get_stats():
    stats = {'all': 0, 'all_tasks': 0, 'on': 0, 'off': 0,
             'cur_tasks': 0, 'loaded': 0, 'free_tasks': 0}
    for server in models.Server.query.all():
        if server.state == settings.SERVER_STATE['off']:
            stats['off'] += 1
            stats['free_tasks'] -= server.max_tasks
            stats['all_tasks'] -= int(server.max_tasks)
        if server.state == settings.SERVER_STATE['on']:
            stats['on'] += 1
            stats['all_tasks'] += int(server.max_tasks)
        if server.max_tasks == server.cur_tasks:
            stats['loaded'] += 1
        stats['all'] += 1
        stats['cur_tasks'] += int(server.cur_tasks)
    stats['free_tasks'] += stats['all_tasks'] - stats['cur_tasks']
    return stats
