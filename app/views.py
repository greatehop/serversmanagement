from sqlalchemy import desc
import datetime

import config
from core import tools
from app import app, db, forms, models, lm, oid

from flask import Flask, render_template, redirect, request, flash, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required


@app.route('/tasks', strict_slashes=False)
@app.route('/tasks/<int:task_id>', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def tasks(task_id=None):
    #TODO: hide task(s) if it is disabled (show for admin's users)
    task_list = models.Task.query.all()
    if task_id is not None:
        task = models.Task.query.get(task_id)

        #TODO: refactor it as plugins
        if task_id == 1:
            form = forms.TaskDeployMOSForm()
            if form.validate_on_submit():
                
                #TODO: repeat if failed
                server = tools.get_server()
                if server is not None:
                    cmd_out = tools.run_task(task.taskname, task.taskfile, server.ip)
                    #TODO: fix cmd_out with \n
                    #TODO: if failed - don't update server state 
                    
                    server_id = server.id                    
                    run_state = config.RUN_STATE['in_progress']
                    db.session.query(models.Server).filter_by(id=server_id).update({'state': config.SERVER_STATE['on_load']})
                    db.session.commit()
                else:
                    server_id = None
                    cmd_out = None
                    run_state = config.RUN_STATE['in_queue']

                task = models.Run(
                    user_id=g.user.id,
                    server_id=server_id,
                    state=run_state,
                    task_id=task_id,
                    cmd_out=cmd_out,
                    datetime = datetime.datetime.utcnow(),
                    attributes = {'deployment_name': form.deployment_name.data,
                                  'iso_url': form.iso_url.data,
                                  'node_count': form.node_count.data,
                                  'slave_node_cpu': form.slave_node_cpu.data,
                                  'slave_node_mem': form.slave_node_mem.data,
                                  'keep_days': form.keep_days.data})
                db.session.add(task)
                db.session.commit()

                #TODO: add update output + env details
                #ssh -f -N -L 11121:10.177.21.3:80 laba

                #TODO: add update run state 
                #db.session.query(models.Run).filter_by(id=run_id).update({'state': config.RUN_STATE['done']})
                #db.session.commit()
                
                return redirect('/runs')
            return render_template('tasks_deploy_mos.html', task=task, form=form)

        elif task_id == 2:
            form = forms.TaskCleanMOSForm()
            if form.validate_on_submit():
                return redirect('/runs')
            return render_template('tasks_clean_mos.html', task=task, form=form)

        else:
            return render_template('tasks.html', task=task)
    else:
        return render_template('tasks.html', task_list=task_list)

@app.route('/runs', methods=['GET', 'POST'], strict_slashes=False)
@app.route('/runs/<int:run_id>', strict_slashes=False)
@login_required
def runs(run_id=None):
    run_list = models.Run.query.order_by(desc(models.Run.id)).limit(config.LAST_RUNS).all()

    #TODO: pagination

    if run_id is not None:
        run = models.Run.query.get(run_id)
        return render_template('runs_details.html', run=run)
    else:
        return render_template('runs.html', run_list=run_list)

@app.route('/servers', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def servers():
    form = forms.ServerForm()
    if form.validate_on_submit():

        #TODO: add run ssh-copy-id

        #TODO: check uniq IP
        server = models.Server(ip=form.ip.data, alias=form.alias.data)
        db.session.add(server)
        db.session.commit()
        return redirect('/servers')

    #TODO: add delete/edit
    #TODO: hide server(s) if it is disabled (show for admin's users)
    #TODO: add verify ssh connection method "uptime"
    server_list = models.Server.query.all()
    return render_template('servers.html', server_list=server_list, form=form)

@app.route('/about', strict_slashes=False)
def about():
    return render_template('about.html')

@app.route('/stats', strict_slashes=False)
@login_required
def stats():
    #TODO: add user/keep days/task?/    
    
    onload_server_list = models.Server.query.filter_by(state=config.SERVER_STATE['on_load']).all()
    empty_server_list = models.Server.query.filter_by(state=config.SERVER_STATE['on']).all()
    return render_template('stats.html', 
                           onload_server_list=onload_server_list,
                           empty_server_list=empty_server_list)

@app.route('/users', strict_slashes=False)
@login_required
def users():
    #TODO: list of user's requests
    user_list = models.User.query.filter_by(state=config.USER_STATE['on']).all()
    return render_template('users.html', user_list=user_list)

@app.route('/', strict_slashes=False)
@app.route('/index', strict_slashes=False)
@login_required
def index():
    run_list = models.Run.query.order_by(desc(models.Run.id)).filter_by(user_id=g.user.id).limit(config.LAST_RUNS).all()
    return render_template('index.html', run_list=run_list)

@app.route('/login', methods = ['GET', 'POST'], strict_slashes=False)
@oid.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect('/index')
    form = forms.LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = True
        return oid.try_login(config.OPENID_PROVIDERS['launchpad']['openid'], ask_for=['nickname', 'email'])
    return render_template('login.html', form=form, providers=config.OPENID_PROVIDERS['launchpad']['url'])

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
        flash('Invalid login. Please try again.')
        return redirect('/login')
    user = models.User.query.filter_by(email=resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        user = models.User(name=nickname, email=resp.email, role=config.USER_ROLE['user'])
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

#TODO: other errorhandlers???