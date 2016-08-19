import flask

from app import extensions as ext
from app.views import common


BLUEPRINTS = (
    common.common,
)


def create_app(blueprints=None):
    app = flask.Flask(__name__)
    app.config.from_object('settings')

    _register_extensions(app)
    if blueprints is None:
        blueprints = BLUEPRINTS

    _register_blueprints(app, blueprints)

    return app


def _register_blueprints(app, blueprints):
    for blueprint in blueprints:
        app.register_blueprint(blueprint)


def _register_extensions(app):
    ext.alembic.init_app(app)
    ext.socketio.init_app(app)

    ext.db.init_app(app)
    ext.db.app = app

    ext.lm.init_app(app)
    ext.lm.login_view = 'common.login'

    ext.oid.init_app(app)