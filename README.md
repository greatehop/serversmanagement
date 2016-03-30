## Description

ServersManagement - "mini-jenkins", allows to run scripts on remote servers via WebUI.


For auth app uses launchpad openid. Default admin user(s) should be set in ADMIN_LIST in settings.py
User's permissions manage in tab "User" (available only for admin users).


In current time tool has only 2 tasks that allows to "deploy/clean" OpenStask Fuel node.


One server allows to execute more than one tasks, for task "deploy_mos" it means more than one env.
Amount of tasks per server manage by admin user in tab "Server" (available only for admin users).


App chooses least loaded server (randomly, if more than one).
If there are no empty servers in current time all "runs" stay in queue.
App's daemon periodically check (DAEMON_TIMEOUT in settings.py) for "free" server.


## Architecture

WebUI: Flask with plugins

DB: SQLAlchemy - MySQL

Remote executor: - Fabric

Steps:

app login -> openid provider -> app -> task -> run -> "EXECUTOR" -> save/show results

where "EXECUTOR" may be one of:
- python.subprocess -> Fabfic -> bash script with args (current implementation)
- python.subprocess -> Fabfic with args
- API Fabric with args
- API Jenkins with args
- ansible/etc ?

## FAQ

Why wouldn't you use "Jenkins" ?

- can't simple and flexible customize job as we want

- can't check some server's state/args/etc BEFORE run job

## Installation

- add user and user on remote servers

- generate ssh key

<pre>
ssh-keygen
</pre>

- copy ssh pub keys to servers

<pre>
ssh-copy-id user@server
</pre>

- setup software

<pre>
apt-get update
apt-get install screen git vim nginx python-pip python-dev python-virtualenv mysql-server libmysqlclient-dev
git clone https://github.com/greatehop/serversmanagement
cd serversmanagement
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt
</pre>

- configurate nginx

<pre>
cp ./tools/nginx.conf /etc/nginx/sites-available/sm.conf
ln -s /etc/nginx/sites-available/sm.conf /etc/nginx/sites-enabled/
nginx -t
service nginx reload
</pre>

- create mysql db/user/grants/init tables

<pre>
service mysql start
mysql -u root -p
CREATE DATABASE dbname;
GRANT ALL PRIVILEGES ON dbname.* TO dbuser@host IDENTIFIED BY password WITH GRANT OPTION;
FLUSH PRIVILEGES;
cd tools; python ./create_db.py
</pre>

- edit settings.py

- configurate remote server

https://docs.fuel-infra.org/fuel-dev/devops.html

<pre>
apt-get update
apt-get install aria2

mkdir -p ~/sm_scripts/iso
cd sm_scripts/
git clone https://github.com/openstack/fuel-qa
virtualenv --system-site-packages venv-mos
. ./venv-mos/bin/activate
cd fuel-qa/
pip install -r ./fuelweb_test/requirements.txt --upgrade

scp ./tools/*_mos.sh user@server:~/sm_scripts/
</pre>

- run app

<pre>
screen -t sm python ./run.py
</pre>

## TODO

- find and fix all issues

<pre>
grep -r 'TODO' ./
</pre>
