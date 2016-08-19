from app.extensions import db
import settings


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    role = db.Column(db.SmallInteger, default=settings.USER_ROLE['user'])
    email = db.Column(db.String(120), index=True, unique=True)
    state = db.Column(db.SmallInteger, default=settings.USER_STATE['on'])
    runs = db.relationship('Run', backref='user', lazy='dynamic')

    @property
    def is_admin(self):
        if self.email in settings.ADMINS or self.role:
            return True
        else:
            return False

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        if self.state:
            return True
        else:
            return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    def __repr__(self):
        return '<User %r>' % (self.name)


class Server(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(15), index=True, unique=True)
    alias = db.Column(db.String(120), index=True)
    state = db.Column(db.SmallInteger, default=settings.SERVER_STATE['on'])
    runs = db.relationship('Run', backref='server', lazy='dynamic')
    max_tasks = db.Column(db.Integer, default=settings.MAX_TASKS)
    cur_tasks = db.Column(db.Integer, default=0)

    def __repr__(self):
        return '<Server %r>' % (self.alias)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), index=True, unique=True)
    desc = db.Column(db.String(150))
    taskfile = db.Column(db.String(150))
    taskname = db.Column(db.String(15), unique=True)
    state = db.Column(db.SmallInteger, default=settings.TASK_STATE['on'])
    runs = db.relationship('Run', backref='task', lazy='dynamic')

    def __repr__(self):
        return '<Task %r>' % (self.name)


class Run(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(15), default=settings.RUN_STATE['in_queue'])
    cmd_out = db.Column(db.Text(length=1048576), default=None)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    server_id = db.Column(db.Integer, db.ForeignKey('server.id'),
                          default=None)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    end_datetime = db.Column(db.DateTime, default=None)
    start_datetime = db.Column(db.DateTime)
    # TODO(hop): to get rid of PickleType
    args = db.Column(db.PickleType, default=None)
