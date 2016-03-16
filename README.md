## DESCRIPTION

ServersManagement - "mini-jenkins", allows to run scripts on remote servers via WebUI.

In current time tool has only 2 tasks that allows to deploy/clean OpenStask Fuel node.

## ARCHITECTURE

WebUI - Flask with plugins

DB - SQLAlchemy - MySQL

Remote executor - Fabric

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

## INSTALL

- generate ssh key

<pre>
ssh-keygen
</pre>

- copy ssh pub keys to servers

<pre>
ssh-copy-id user@server
</pre>

- add user and user on remote servers

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

- run app

<pre>
screen -t sm python ./run.py
</pre>

## TODO

- find and fix all issues

<pre>
grep -r 'TODO' ./
</pre>