#!/usr/bin/python

from migrate.versioning import api
from config import SQLALCHEMY_DATABASE_URI
from config import SQLALCHEMY_MIGRATE_REPO
from app import db
import os.path

db.create_all()
if not os.path.exists(SQLALCHEMY_MIGRATE_REPO):
    api.create(SQLALCHEMY_MIGRATE_REPO, 'database repository')
    api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
else:
    api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, api.version(SQLALCHEMY_MIGRATE_REPO))

#temp for tasks
from app import models
task = models.Task(name='deploy_mos', desc='', taskfile='./fabfile.py', taskname='deploy_mos')
db.session.add(task)
db.session.commit()

task2 = models.Task(name='clean_mos', desc='', taskfile='./fabfile.py', taskname='clean_mos')
db.session.add(task2)
db.session.commit()
