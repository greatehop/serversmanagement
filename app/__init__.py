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

#TODO: need fix logging
if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('tmp/sm.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)