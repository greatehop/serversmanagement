import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = True

CSRF_ENABLED = True
SECRET_KEY = 'you-will-nasdfasdasdfasdfasdever-guess'

USER_ROLE = {'user': 0, 'admin': 1}

USER_STATE = {'on': 1, 'off': 0}
SERVER_STATE = {'off': 0, 'on': 1, 'on_load': 2}
RUN_STATE = {'in_queue': 0, 'in_progress': 1, 'done': 2, 'canceled': 3}
TASK_STATE = {'off': 0, 'on': 1}

OPENID_PROVIDERS = {'launchpad': { 'url': 'https://launchpad.net/people/+me', 
                                  'openid': 'https://login.launchpad.net/+openid'}}

# show only N last runs
LAST_RUNS = 20

# remote ssh user for tasks
SSH_USER = 'jenkins'
SSH_PORT = 22

#in seconds
SCHEDULER_TIMEOUT = 60