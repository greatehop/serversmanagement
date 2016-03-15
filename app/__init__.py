async_mode = None

if async_mode is None:
    try:
        import eventlet
        async_mode = 'eventlet'
    except ImportError:
        pass

    if async_mode is None:
        try:
            from gevent import monkey
            async_mode = 'gevent'
        except ImportError:
            pass

    if async_mode is None:
        async_mode = 'threading'

if async_mode == 'eventlet':
    import eventlet
    eventlet.monkey_patch()
elif async_mode == 'gevent':
    from gevent import monkey

import os
from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.openid import OpenID
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.socketio import SocketIO, emit

app = Flask(__name__)
app.config.from_object('settings')
socketio = SocketIO(app, async_mode=async_mode)
db = SQLAlchemy(app)
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
oid = OpenID(app, os.path.realpath('tmp'))

from app import views, models