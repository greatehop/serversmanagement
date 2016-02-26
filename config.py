CSRF_ENABLED = True
SECRET_KEY = 'you-will-nasdfasdasdfasdfasdever-guess'


import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = True

# show only N last runs
last_runs = 10

#ssh_user = jenkins
#ssh_port = 22

user_role = {'user': 0, 'admin': 1}

user_state = {'on': 1, 'off': 0}
server_state = {'off': 0, 'on': 1, 'on_load': 2}
run_state = {'in_queue': 0, 'in_progress': 1, 'done': 2, 'canceled': 3}
task_state = {'off': 0, 'on': 1}