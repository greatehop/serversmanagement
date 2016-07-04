import logging
import logging.config
import os
import yaml

from serversmanagement.app import app as flask_app
from serversmanagement.app import extensions as ext
from serversmanagement.tools import core


app = flask_app.create_app()


def setup_logging(config_path):
    """Setup logging"""
    default_level = logging.INFO

    if not os.path.exists('logs'):
        os.makedirs('logs')

    if os.path.exists(config_path):
        with open(config_path, 'rt') as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

if __name__ == '__main__':
    config_path = 'logging.yaml'
    setup_logging(config_path=config_path)

    # run daemon in background
    daemon = core.Scheduler()
    daemon.start()

    # run web app
    ext.socketio.run(app, host='0.0.0.0', port=5000)
