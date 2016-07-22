from datetime import datetime
import logging
import re
import traceback

import flask
import flask_login
import sqlalchemy

from serversmanagement.app.database import models
from serversmanagement.app import extensions as ext
from serversmanagement.app import forms
from serversmanagement.app import servermanager
from serversmanagement import settings
from serversmanagement.tools import core


fuel_ver = re.compile(
    '(?:fuel|MirantisOpenStack)\-((\d+\.\d+)(?:(?:\-mos)?-\d+)?)'
)

logger = logging.getLogger(__name__)

common = flask.Blueprint('common', __name__)


@common.route('/tasks', strict_slashes=False)
@common.route('/tasks/<int:task_id>', methods=['GET', 'POST'],
              strict_slashes=False)
@flask_login.login_required
def tasks(task_id=None):
    # TODO(hoo): refactor tasks as plugins

    # TODO(hop): add "run again with the same arguments"

    task_list = models.Task.query.all()
    if task_id is not None:
        task = models.Task.query.get(task_id)

        if not task:
            return flask.render_template('tasks.html', task_list=task_list)

        if task.name == 'deploy_mos':
            form = forms.TaskDeployMOSForm()

            if form.validate_on_submit():
                # get or generate deployment name and mos version
                venv = 'venv-mos'
                ver = fuel_ver.findall(form.iso_url.data)
                if ver:
                    iso = ver[0][0]
                    if ver[0][1] in ['6.1', '7.0', '8.0']:
                        venv += ver[0][1]
                else:
                    iso = datetime.utcnow().strftime('%H_%M_%S_%d.%m.%Y')

                if form.deploy_name.data:
                    deploy_name = '{0}_{1}'.format(
                        flask.g.user.name, form.deploy_name.data)
                else:
                    deploy_name = '{0}_{1}'.format(flask.g.user.name, iso)

                # ironic support
                ironic_enabled = 'false'
                if int(form.ironic_nodes_count.data):
                    ironic_enabled = 'true'

                # save run to db
                run = models.Run(
                    user_id=flask.g.user.id,
                    task_id=task_id,
                    start_datetime=datetime.utcnow(),
                    args={'deploy_name': deploy_name,
                          'iso_url': form.iso_url.data,
                          'nodes_count': form.nodes_count.data,
                          'slave_node_cpu': form.slave_node_cpu.data,
                          'slave_node_memory': form.slave_node_memory.data,
                          'ironic_nodes_count': form.ironic_nodes_count.data,
                          'ironic_enabled': ironic_enabled,
                          'keep_days': form.keep_days.data,
                          'venv': venv})
                ext.db.session.add(run)
                ext.db.session.commit()

                # Note: we have already added it to the database
                # Why we need to run it the second time?

                # get server and execute run
                server = servermanager.reserve_server(run)
                if server:
                    core.run_task(task, server, run)

                return flask.redirect('/runs')
            return flask.render_template('tasks_deploy_mos.html',
                                         task=task, form=form)

        elif task.name == 'clean_mos':
            form = forms.TaskCleanMOSForm()

            # generate alive envs for current user
            filter = {'state': settings.RUN_STATE['done'],
                      'user_id': flask.g.user.id,
                      'task_id': 1}

            # generate all alive envs for admin user
            if flask.g.user.is_admin:
                filter.pop('user_id')

            run_list = models.Run.query.order_by(
                sqlalchemy.desc(models.Run.id)).filter_by(**filter).all()

            if run_list:
                form.deploy_name.choices = [
                    (run.id, run.args['deploy_name']) for run in run_list]
                if form.validate_on_submit():
                    # get server from existing run
                    run_id = int(form.deploy_name.data)
                    exist_run = [i for i in run_list if i.id == run_id][0]
                    server = models.Server.query.get(exist_run.server_id)

                    # save run to db
                    run = models.Run(
                        user_id=flask.g.user.id, task_id=task_id,
                        args={'deploy_name': exist_run.args['deploy_name'],
                              'venv': exist_run.args['venv']},
                        start_datetime=datetime.utcnow())

                    # execute task
                    core.run_task(task, server, run)

                    # mark run as deleted and decrease cur_tasks
                    server.erase_env(exist_run)

                    return flask.redirect('/runs')
            else:
                form = None
        return flask.render_template('tasks_clean_mos.html',
                                     task=task, form=form)
    else:
        return flask.render_template('tasks.html', task_list=task_list)


@common.route('/runs', methods=['GET', 'POST'], strict_slashes=False)
@common.route('/runs/<int:run_id>', strict_slashes=False)
@flask_login.login_required
def runs(run_id=None):

    # TODO(hop): pagination
    # TODO(hop): share run/task???
    # TODO(hop): if run in q - update start_datetime

    if run_id is not None:
        run = models.Run.query.get(run_id)

        form = forms.TaskCleanMOSForm()
        form.deploy_name.choices = [(run.id, run.args['deploy_name'])]
        """
        if form.validate_on_submit():
            # get server from existing run
            run_id = int(form.deploy_name.data)
            exist_run = [i for i in run_list if i.id == run_id][0]

            # save run to db
            run = models.Run(
                user_id=g.user.id, task_id=task_id,
                args={'deploy_name': exist_run.args['deploy_name']},
                start_datetime=datetime.utcnow())
            db.session.add(run)
            db.session.commit()

            # execute task
            core.run_task(task, server, run)

            # mark existing run as removed
            db.session.query(models.Run).filter_by(
                id=exist_run.id).update(
                {'state': settings.RUN_STATE['removed']})
            db.session.commit()

            # decrease current number of tasks
            core.update_server({'id': exist_run.server_id}, add=False)
        """
        return flask.render_template('runs_details.html', run=run, form=form)
    else:
        # show runs only with "done/in_progress/in_queue" states
        run_list = models.Run.query.filter(
            models.Run.task_id == 1,
            models.Run.state != settings.RUN_STATE['removed']).order_by(
            sqlalchemy.desc(models.Run.id)).limit(settings.LAST_RUNS).all()
        return flask.render_template('runs.html', run_list=run_list)


@common.route('/servers/del/<int:server_id>', methods=['POST'],
              strict_slashes=False)
@flask_login.login_required
def servers_del(server_id=None):
    if not flask.g.user.is_admin:
        return flask.render_template('404.html')

    # TODO(hop): block delete if server has runs
    ext.db.session.execute(models.Run.__table__.delete().where(
        models.Run.server_id == server_id))
    ext.db.session.query(models.Server).filter_by(
        id=int(server_id)).delete()
    ext.db.session.commit()

    return flask.redirect('/servers')


@common.route('/servers', methods=['GET', 'POST'], strict_slashes=False)
@common.route('/servers/<int:server_id>',
              methods=['GET', 'POST'], strict_slashes=False)
@flask_login.login_required
def servers(server_id=None):
    # TODO(hop): add test ssh connection

    if not flask.g.user.is_admin:
        return flask.render_template('404.html')

    form = forms.ServerForm()
    if server_id is not None:
        if form.validate_on_submit():
            # edit server settings
            ext.db.session.query(models.Server).filter_by(id=server_id).update(
                {'ip': form.ip.data,
                 'alias': form.alias.data,
                 'state': form.is_active.data,
                 'max_tasks': form.max_tasks.data})
            ext.db.session.commit()
            return flask.redirect('/servers')
        else:
            # show server settings
            server = models.Server.query.get(server_id)
            if server:
                form.id.data = server.id
                form.ip.data = server.ip
                form.alias.data = server.alias
                form.is_active.data = server.state
                form.max_tasks.data = server.max_tasks
            return flask.render_template('servers_details.html',
                                         server=server,
                                         form=form)
    else:
        if form.validate_on_submit():
            # add server with settings
            server = models.Server(ip=form.ip.data,
                                   alias=form.alias.data,
                                   state=form.is_active.data,
                                   max_tasks=form.max_tasks.data)
            ext.db.session.add(server)
            ext.db.session.commit()
            return flask.redirect('/servers')
        else:
            server_list = models.Server.query.all()
            return flask.render_template('servers.html',
                                         server_list=server_list,
                                         form=form)


@common.route('/about', strict_slashes=False)
def about():
    return flask.render_template('about.html')


@common.route('/stats', strict_slashes=False)
@flask_login.login_required
def stats():
    cur_time = datetime.utcnow()

    # get info who loaded servers
    server_list = models.Server.query.join(models.Run).join(
        models.User).join(models.Task).add_columns(
            models.Server.ip, models.Server.alias, models.Server.state,
            models.Server.max_tasks, models.Server.cur_tasks,
            models.User.name, models.Run.id).filter(
                models.Run.state == settings.RUN_STATE['done'],
                models.Run.task_id == 1).all()

    # get servers state
    stats = core.get_stats()

    return flask.render_template('stats.html', server_list=server_list,
                                 cur_time=cur_time, stats=stats)


@common.route('/users', strict_slashes=False)
@common.route('/users/<int:user_id>', methods=['GET', 'POST'],
              strict_slashes=False)
@flask_login.login_required
def users(user_id=None):
    # TODO(hop): change way to log in

    # TODO(hop): add info about admin user in settings

    if not flask.g.user.is_admin:
        return flask.render_template('404.html')
    form = forms.UserForm()
    if user_id is not None:
        if form.validate_on_submit():
            # edit user setting
            ext.db.session.query(models.User).filter_by(id=user_id).update(
                {'state': form.is_active.data,
                 'role': form.is_admin.data})
            ext.db.session.commit()

            return flask.redirect('/users')
        else:
            # show user setting
            user = models.User.query.get(user_id)
            if user:
                form.is_active.data = user.is_active
                form.is_admin.data = user.is_admin
            return flask.render_template('users_details.html',
                                         user=user, form=form)
    else:
        user_list = models.User.query.all()
        return flask.render_template('users.html',
                                     user_list=user_list, form=form)


@common.route('/', strict_slashes=False)
@common.route('/index', strict_slashes=False)
@flask_login.login_required
def index():
    run_list = models.Run.query.order_by(
        sqlalchemy.desc(models.Run.id)).filter_by(
        user_id=flask.g.user.id).limit(settings.LAST_RUNS).all()

    # get servers state
    stats = core.get_stats()

    return flask.render_template('index.html', run_list=run_list, stats=stats)


@common.route('/kill/<int:pid>', methods=['POST'], strict_slashes=False)
@flask_login.login_required
def kill(pid=None):
    core.kill(int(pid))
    return flask.redirect('/runs')


@common.route('/login', methods=['GET', 'POST'], strict_slashes=False)
@ext.oid.loginhandler
def login():
    if flask.g.user is not None and flask.g.user.is_authenticated:
        return flask.redirect('/index')
    form = forms.LoginForm()
    if form.validate_on_submit():
        flask.session['remember_me'] = True
        return ext.oid.try_login(settings.OPENID['launchpad']['openid'],
                                 ask_for=['nickname', 'email'])
    return flask.render_template('login.html', form=form,
                                 providers=settings.OPENID['launchpad']['url'])


@common.route('/logout', strict_slashes=False)
def logout():
    flask_login.logout_user()
    return flask.redirect('/login')


@ext.lm.user_loader
def load_user(id):
    return models.User.query.get(int(id))


@common.before_request
def before_request():
    flask.g.user = flask_login.current_user


@ext.oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "":
        return flask.redirect('/login')
    user = models.User.query.filter_by(email=resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        user = models.User(name=nickname, email=resp.email,
                           role=settings.USER_ROLE['user'])
        ext.db.session.add(user)
        ext.db.session.commit()
    remember_me = False
    if 'remember_me' in flask.session:
        remember_me = flask.session['remember_me']
        flask.session.pop('remember_me', None)
    flask_login.login_user(user, remember=remember_me)
    return flask.redirect(flask.request.args.get('next') or '/index')


@common.errorhandler(404)
def page_not_found(e):
    return flask.render_template('404.html'), 404


@common.errorhandler(Exception)
def internal_error(e):
    logger.error(traceback.format_exc())
    return flask.render_template('500.html'), 500
