import sys
sys.path.insert(0, '../')

from app import extensions as ext
from app import models


ext.db.create_all()

# create tasks
task_deploy_mos = models.Task(name='deploy_mos',
                              taskfile='./app/fabfile.py',
                              taskname='deploy_mos')
task_clean_mos = models.Task(name='clean_mos',
                             taskfile='./app/fabfile.py',
                             taskname='clean_mos')
ext.db.session.add(task_deploy_mos)
ext.db.session.add(task_clean_mos)
ext.db.session.commit()
