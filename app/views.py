import config
from core import tools
from app import app, db, forms, models

from flask import Flask, render_template, redirect, request, flash
from sqlalchemy import desc


@app.route('/tasks', strict_slashes=False)
@app.route('/tasks/<int:task_id>', methods=['GET', 'POST'], strict_slashes=False)
def tasks(task_id=None):
    #TODO: hide task(s) if it is disabled (show for admin users)
    task_list = models.Task.query.all()
    if task_id is not None:
        task = models.Task.query.get(task_id)

        #TODO: refactor it as pliugins
        
        #TODO: fix it
        if task_id == 1:
            form = forms.TaskDeployMOSForm()
            if form.validate_on_submit():
                
                #TODO: class???
                server_id = tools.get_server()
                if server_id is not None:
                    run_state = config.run_state['in_progress']
                    db.session.query(models.Server).filter_by(id=server_id).update({'state': config.server_state['on_load']})
                    db.session.commit()
                else:
                    run_state = config.run_state['in_queue']
                    
                #TODO: fix task auth
                task_auth = 'dev'
                cmd_out = tools.run_task(task.taskname, task.taskfile, task_auth)

                #TODO: fix cmd_out with \n
                
                task = models.Run(
                    #user_id=user_id,
                    server_id=server_id,
                    state=run_state,
                    task_id=task_id, 
                    cmd_out=cmd_out,
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

                #TODO: add update task state 
                #TODO: update server state by ID
                
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
def runs(run_id=None):
    #TODO: add filter by your or running runs
    run_list = models.Run.query.order_by(desc(models.Run.id)).limit(config.last_runs).all()
    
    #TODO: pagination 
    
    #TODO: fix wrong request runs/1335d
    
    #TODO: all runs, your runs
    
    if run_id is not None:
        run = models.Run.query.get(run_id)
        return render_template('runs_details.html', run=run)
    else:
        return render_template('runs.html', run_list=run_list)

@app.route('/servers', methods=['GET', 'POST'], strict_slashes=False)
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
    #TODO: hide server(s) if it is disabled (show for admin users)
    server_list = models.Server.query.all()
    return render_template('servers.html', server_list=server_list, form=form)

@app.route('/users', strict_slashes=False)
def users():
    #TODO: need auth via openID
    #TODO: list of user's requests
    return render_template('users.html')

@app.route('/', strict_slashes=False)
@app.route('/home', strict_slashes=False)
def index():
    #TODO: openID auth via launchpad https://launchpad.net/~your_nickname
    return render_template('index.html')

@app.route('/about', strict_slashes=False)
def about():
    return render_template('about.html')

@app.route('/stats', strict_slashes=False)
def stats():
    return render_template('stats.html')