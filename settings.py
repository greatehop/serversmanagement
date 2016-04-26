DEBUG = False

SQLALCHEMY_DATABASE_URI = 'mysql://sm:<CHANGE_ME>@localhost/sm'
SQLALCHEMY_TRACK_MODIFICATIONS = False

CSRF_ENABLED = True
SECRET_KEY = '<CHANGE_ME>'

# show only N last runs
LAST_RUNS = 30

# remote ssh user for tasks
SSH_USER = 'jenkins'
SSH_PORT = 22

# in seconds
DAEMON_TIMEOUT = 10

# max count of running tasks per servers
MAX_TASKS = 1

# tasks args
NODES_COUNT = 6
KEEP_DAYS = 0

# admin list
# (needs only for first log in, manage by user -> is_admin)
ADMINS = ['user@domain.com']

USER_ROLE = {'user': 0, 'admin': 1}

USER_STATE = {'off': 0, 'on': 1}
SERVER_STATE = {'off': 0, 'on': 1}
TASK_STATE = {'off': 0, 'on': 1}
RUN_STATE = {'in_queue': 0, 'in_progress': 1, 'done': 2,
             'canceled': 3, 'removed': 4}

OPENID = {'launchpad':
          {'url': 'https://launchpad.net/people/+me',
                  'openid': 'https://login.launchpad.net/+openid'}}