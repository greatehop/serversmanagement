DESCRIPTION:

ServersManagement - "mini-jenkins", allows to run scripts on remote servers via WebUI.

ACRH:

WebUI - Flask with plugins
DB - SQLAlchemy - MySQL
remote commands executor - fabric

INSTALL:
- create mysql user/grants

create database <db_name>;
GRANT ALL PRIVILEGES ON <db_name>.* TO '<db_user>'@'<host>' IDENTIFIED BY '<password>' WITH GRANT OPTION;
flush privileges;

- add user and user on remote servers

- generate ssh key

ssh-keygen

- copy ssh pub keys to servers

ssh-copy-id <user>@<server>

- setup software

git clone https://github.com/greatehop/serversmanagement
cd serversmanagement
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt

- edit settings.py

- run configurator for "(deploy/clean)_mos" task's script

- run app

TODO:
- find and fix all issues

grep -r 'TODO' ./