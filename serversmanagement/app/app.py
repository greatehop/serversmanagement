import flask

from serversmanagement.app import extensions as ext
from serversmanagement.app.views import common


__all__ = ('create_app',)

BLUEPRINTS = (
    common.common,
)


def create_app(config_file=None, blueprints=None):
    app = flask.Flask(__name__)
    app.config.from_object('serversmanagement.settings')

    _extensions_fabrics(app)

    if blueprints is None:
        blueprints = BLUEPRINTS

    _blueprints_fabrics(app, blueprints)

    return app


def _blueprints_fabrics(app, blueprints):
    for blueprint in blueprints:
        app.register_blueprint(blueprint)


def _extensions_fabrics(app):
    ext.alembic.init_app(app)
    ext.socketio.init_app(app)

    ext.db.init_app(app)
    ext.db.app = app

    ext.lm.init_app(app)
    ext.lm.login_view = 'common.login'

    ext.oid.init_app(app)
