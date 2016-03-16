#!/usr/bin/python

import sys
sys.path.insert(0, '../')
from app import db, models

db.create_all()

# create tasks
task_deploy_mos = models.Task(name='deploy_mos', desc='', 
                              taskfile='./app/fabfile.py', taskname='deploy_mos')
task_clean_mos = models.Task(name='clean_mos', desc='',
                              taskfile='./app/fabfile.py', taskname='clean_mos')
db.session.add(task_deploy_mos)
db.session.add(task_clean_mos)
db.session.commit()
