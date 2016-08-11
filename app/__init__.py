import logging
from logging.handlers import RotatingFileHandler

import appcreator

try:
    import eventlet
    async_mode = 'eventlet'
    eventlet.monkey_patch()
except ImportError:
    try:
        from gevent import monkey
        async_mode = 'gevent'
    except ImportError:
        async_mode = 'threading'

app = appcreator.create_app()

# TODO(hop): need fix logging
if not app.debug:
    file_handler = RotatingFileHandler('sm.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
