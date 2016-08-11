import os

import eventlet
import flask_login
import flask_openid
import flask_socketio
import flask_sqlalchemy


async_mode = 'eventlet'
eventlet.monkey_patch()

socketio = flask_socketio.SocketIO(async_mode=async_mode)
db = flask_sqlalchemy.SQLAlchemy()

lm = flask_login.LoginManager()

oid = flask_openid.OpenID(os.path.realpath('tmp'))