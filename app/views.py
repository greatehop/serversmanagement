import settings
from tools import core
from app import app, db, forms, models, lm, oid

from datetime import datetime
import re
from flask import render_template, redirect, request, \
                  session, g
from flask.ext.login import login_user, logout_user, \
                            current_user, login_required
from sqlalchemy import desc


fuel_ver = re.compile('(?:fuel|MirantisOpenStack)\-((\d+\.\d+)(?:(?:\-mos)?-\d+)?)')


@app.route('/tasks', strict_slashes=False)
@app.route('/tasks/<int:task_id>', methods=['GET', 'POST'],
           strict_slashes=False)
@login_required
def tasks(task_id=None):
    # TODO(hoo): refactor tasks as plugins

    # TODO(hop): add "run again with the same arguments"

    task_list = models.Task.query.all()
    if task_id is not None:
        task = models.Task.query.get(task_id)

        if not task:
            return render_template('tasks.html', task_list=task_list)

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
                    deploy_name = '%s_%s' % (
                        g.user.name, form.deploy_name.data)
                else:
                    deploy_name = '%s_%s' % (g.user.name, iso)

                # ironic support
                ironic_enabled = 'false'
                if int(form.ironic_nodes_count.data):
                    ironic_enabled = 'true'

                # save run to db
                run = models.Run(
                    user_id=g.user.id,
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
                db.session.add(run)
                db.session.commit()

                # get server and execute run
                server = core.get_server()
                if server:
                    core.run_task(task, server, run)

                return redirect('/runs')
            return render_template('tasks_deploy_mos.html',
                                   task=task, form=form)

        elif task.name == 'clean_mos':
            form = forms.TaskCleanMOSForm()

            # generate alive envs for current user
            filter = {'state': settings.RUN_STATE['done'],
                      'user_id': g.user.id,
                      'task_id': 1}

            # generate all alive envs for admin user
            if g.user.is_admin:
                filter.pop('user_id')

            run_list = models.Run.query.order_by(
                desc(models.Run.id)).filter_by(**filter).all()

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
                        user_id=g.user.id, task_id=task_id,
                        args={'deploy_name': exist_run.args['deploy_name'],
                              'venv': exist_run.args['venv']},
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

                    return redirect('/runs')
            else:
                form = None
        return render_template('tasks_clean_mos.html', task=task, form=form)
    else:
        return render_template('tasks.html', task_list=task_list)


@app.route('/runs', methods=['GET', 'POST'], strict_slashes=False)
@app.route('/runs/<int:run_id>', strict_slashes=False)
@login_required
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
        return render_template('runs_details.html', run=run, form=form)
    else:
        # show runs only with "done/in_progress/in_queue" states
        run_list = models.Run.query.filter(
            models.Run.task_id == 1,
            models.Run.state != settings.RUN_STATE['removed']).order_by(
            desc(models.Run.id)).limit(settings.LAST_RUNS).all()
        return render_template('runs.html', run_list=run_list)


@app.route('/servers/del/<int:server_id>', methods=['POST'],
           strict_slashes=False)
@login_required
def servers_del(server_id=None):
    if not g.user.is_admin:
        return render_template('404.html')

    # TODO(hop): block delete if server has runs
    db.session.execute(models.Run.__table__.delete().where(
        models.Run.server_id == server_id))
    db.session.query(models.Server).filter_by(
        id=int(server_id)).delete()
    db.session.commit()

    return redirect('/servers')


@app.route('/servers', methods=['GET', 'POST'], strict_slashes=False)
@app.route('/servers/<int:server_id>',
           methods=['GET', 'POST'], strict_slashes=False)
@login_required
def servers(server_id=None):
    # TODO(hop): add test ssh connection

    if not g.user.is_admin:
        return render_template('404.html')

    form = forms.ServerForm()
    if server_id is not None:
        if form.validate_on_submit():
            # edit server settings
            db.session.query(models.Server).filter_by(id=server_id).update(
                {'ip': form.ip.data,
                 'alias': form.alias.data,
                 'state': form.is_active.data,
                 'max_tasks': form.max_tasks.data})
            db.session.commit()
            return redirect('/servers')
        else:
            # show server settings
            server = models.Server.query.get(server_id)
            if server:
                form.id.data = server.id
                form.ip.data = server.ip
                form.alias.data = server.alias
                form.is_active.data = server.state
                form.max_tasks.data = server.max_tasks
            return render_template('servers_details.html',
                                   server=server,
                                   form=form)
    else:
        if form.validate_on_submit():
            # add server with settings
            server = models.Server(ip=form.ip.data,
                                   alias=form.alias.data,
                                   state=form.is_active.data,
                                   max_tasks=form.max_tasks.data)
            db.session.add(server)
            db.session.commit()
            return redirect('/servers')
        else:
            server_list = models.Server.query.all()
            return render_template('servers.html',
                                   server_list=server_list, form=form)


@app.route('/about', strict_slashes=False)
def about():
    return render_template('about.html')


@app.route('/stats', strict_slashes=False)
@login_required
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

    return render_template('stats.html', server_list=server_list,
                           cur_time=cur_time, stats=stats)


@app.route('/users', strict_slashes=False)
@app.route('/users/<int:user_id>', methods=['GET', 'POST'],
           strict_slashes=False)
@login_required
def users(user_id=None):
    # TODO(hop): change way to log in

    # TODO(hop): add info about admin user in settings

    if not g.user.is_admin:
        return render_template('404.html')
    form = forms.UserForm()
    if user_id is not None:
        if form.validate_on_submit():
            # edit user setting
            db.session.query(models.User).filter_by(id=user_id).update(
                {'state': form.is_active.data,
                 'role': form.is_admin.data})
            db.session.commit()

            return redirect('/users')
        else:
            # show user setting
            user = models.User.query.get(user_id)
            if user:
                form.is_active.data = user.is_active
                form.is_admin.data = user.is_admin
            return render_template('users_details.html',
                                   user=user, form=form)
    else:
        user_list = models.User.query.all()
        return render_template('users.html',
                               user_list=user_list, form=form)


@app.route('/', strict_slashes=False)
@app.route('/index', strict_slashes=False)
@login_required
def index():
    run_list = models.Run.query.order_by(
        desc(models.Run.id)).filter_by(
        user_id=g.user.id).limit(settings.LAST_RUNS).all()

    # get servers state
    stats = core.get_stats()

    return render_template('index.html', run_list=run_list, stats=stats)


@app.route('/kill/<int:pid>', methods=['POST'], strict_slashes=False)
@login_required
def kill(pid=None):
    core.kill(int(pid))
    return redirect('/runs')


@app.route('/login', methods=['GET', 'POST'], strict_slashes=False)
@oid.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect('/index')
    form = forms.LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = True
        return oid.try_login(settings.OPENID['launchpad']['openid'],
                             ask_for=['nickname', 'email'])
    return render_template('login.html', form=form,
                           providers=settings.OPENID['launchpad']['url'])


@app.route('/logout', strict_slashes=False)
def logout():
    logout_user()
    return redirect('/login')


@lm.user_loader
def load_user(id):
    return models.User.query.get(int(id))


@app.before_request
def before_request():
    g.user = current_user


@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "":
        return redirect('/login')
    user = models.User.query.filter_by(email=resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        user = models.User(name=nickname, email=resp.email,
                           role=settings.USER_ROLE['user'])
        db.session.add(user)
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember=remember_me)
    return redirect(request.args.get('next') or '/index')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(Exception)
def internal_error(e):
    return render_template('500.html'), 500
