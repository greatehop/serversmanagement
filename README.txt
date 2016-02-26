DESCRIPTION: 

ServersManagment - minijenkins, allows to run script on remote servers via web UI 

INSTALL:

- add user and user on remote servers

- generate ssh key
ssh-keygen

- copy ssh pub keys to servers
ssh-copy-id <user@server>

- venv

- edit config.py

- run task's script 
needs for configurate remote servers
https://docs.fuel-infra.org/fuel-dev/devops.html  

- run daemon?? 
supervisor

- wsgi


REQEEREMENTS:

"""
Flask-SocketIO
Flask-sqlalchemy
Flask-WTF
flask_ext_migrate
python-migrate
sqlalchemy-migrate
"""

#TODO: fix it!
How to add new task:

- create fabric file with task
- add task to db (example in create.db)
- create logic in app/view.py
- create forms in app/forms.py
- create template in app/tasks_<task_name>.html

#TODO:
- add db scheme
- project scheme

CONTACTS:

Alexander Gubanov
skype: joinordie
email: ogubanov@mirantis.com