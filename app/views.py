import settings
from tools import core
from app import app, db, forms, models, lm, oid

import datetime
from flask import Flask, render_template, redirect, request, \
                  session, request, g
from flask.ext.login import login_user, logout_user, \
                            current_user, login_required
from sqlalchemy import desc


@app.route('/tasks', strict_slashes=False)
@app.route('/tasks/<int:task_id>',
           methods=['GET', 'POST'], strict_slashes=False)
@login_required
def tasks(task_id=None):
    #TODO: hide task(s) if it is disabled (show for admin's users)

    #TODO: refactor tasks as plugins

    #TODO: add "run again with the same arguments"

    task_list = models.Task.query.all()
    if task_id is not None:
        task = models.Task.query.get(task_id)

        if not task:
            return render_template('tasks.html', task_list=task_list)

        if task.name == 'deploy_mos':
            form = forms.TaskDeployMOSForm()
            if form.validate_on_submit():

                # save run to db
                run = models.Run(
                    user_id=g.user.id,
                    task_id=task_id,
                    start_datetime=datetime.datetime.utcnow(),
                    args={'deploy_name': '%s_%s' % (g.user.name,
                                                    form.deploy_name.data),
                          'iso_url': form.iso_url.data,
                          'node_count': form.node_count.data,
                          'slave_node_cpu': form.slave_node_cpu.data,
                          'slave_node_mem': form.slave_node_mem.data,
                          'keep_days': form.keep_days.data})
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
            #TODO: show all envs for admin

            form = forms.TaskCleanMOSForm()

            # generate alive envs (state "done") for current user
            # and all alive envs for admin
            state_done = settings.RUN_STATE['done']
            run_list = models.Run.query.order_by(
                    desc(models.Run.id)).filter_by(
                    user_id=g.user.id, state=state_done, task_id=1).all()

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
                        args={'deploy_name': exist_run.args['deploy_name']},
                        start_datetime=datetime.datetime.utcnow())
                    db.session.add(run)
                    db.session.commit()

                    # execute run
                    core.run_task(task, server, run)

                    # mark existing run as removed
                    db.session.query(models.Run).filter_by(
                        id=exist_run.id).update(
                        {'state': settings.RUN_STATE['removed']})
                    db.session.commit()

                    # decrease current number of tasks
                    db.session.query(models.Server).filter_by(
                        id=exist_run.server_id).update(
                        {'cur_tasks': models.Server.cur_tasks-1})
                    db.session.commit()

                    return redirect('/runs')
            else:
                form = None
        return render_template('tasks_clean_mos.html',
                                task=task, form=form)
    else:
        return render_template('tasks.html', task_list=task_list)

@app.route('/runs', methods=['GET', 'POST'], strict_slashes=False)
@app.route('/runs/<int:run_id>', strict_slashes=False)
@login_required
def runs(run_id=None):
    run_list = models.Run.query.order_by(
        desc(models.Run.id)).limit(settings.LAST_RUNS).all()

    #TODO: pagination

    if run_id is not None:
        run = models.Run.query.get(run_id)

        #TODO: share run/task
        #TODO: if run in q - update start_datetime
        return render_template('runs_details.html', run=run)
    else:
        return render_template('runs.html', run_list=run_list)

@app.route('/servers', methods=['GET', 'POST'], strict_slashes=False)
@app.route('/servers/<int:server_id>',
           methods=['GET', 'POST'], strict_slashes=False)
@login_required
def servers(server_id=None):
    #TODO: add delete
    #TODO: block delete/disable if server has taks/runs
    #Server.query.filter_by(id=server_id).delete()

    #TODO: add test ssh connection
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
    #TODO: add user/keep days/task/

    state_on = settings.SERVER_STATE['on']
    empty_server_list = models.Server.query.filter_by(
        state=state_on, cur_tasks=0).all()
    return render_template('stats.html',
                           empty_server_list=empty_server_list)

@app.route('/users', strict_slashes=False)
@app.route('/users/<int:user_id>',
           methods=['GET', 'POST'], strict_slashes=False)
@login_required
def users(user_id=None):
    #TODO: change way to log in

    #TODO: add info about admin user in setting

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
        state_on = settings.USER_STATE['on']
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
    return render_template('index.html', run_list=run_list)

@app.route('/login', methods = ['GET', 'POST'], strict_slashes=False)
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

@app.errorhandler(500)
def internal_error(e):
    return render_template('404.html'), 500

#TODO: other errorhandlers???

#TODO: add update keep days