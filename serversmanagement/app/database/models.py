import serversmanagement.app.extensions as ext
from serversmanagement import settings


class User(ext.db.Model):
    id = ext.db.Column(ext.db.Integer, primary_key=True)
    name = ext.db.Column(ext.db.String(64), index=True, unique=True)
    role = ext.db.Column(ext.db.SmallInteger,
                         default=settings.USER_ROLE['user'])
    email = ext.db.Column(ext.db.String(120), index=True, unique=True)
    state = ext.db.Column(ext.db.SmallInteger,
                          default=settings.USER_STATE['on'])
    runs = ext.db.relationship('Run', backref='user', lazy='dynamic')

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
        return '<User {0}>'.format(self.name)


class Server(ext.db.Model):
    id = ext.db.Column(ext.db.Integer, primary_key=True)
    ip = ext.db.Column(ext.db.String(15), index=True, unique=True)
    alias = ext.db.Column(ext.db.String(120), index=True)
    state = ext.db.Column(ext.db.SmallInteger,
                          default=settings.SERVER_STATE['on'])
    runs = ext.db.relationship('Run', backref='server', lazy='dynamic')
    max_tasks = ext.db.Column(ext.db.Integer, default=settings.MAX_TASKS)
    cur_tasks = ext.db.Column(ext.db.Integer, default=0)

    def __repr__(self):
        return '<Server {0}>'.format(self.alias)

    @property
    def used_ram(self):
        reserved_ram = 0

        runs = [run for run in self.runs
                if int(run.state) in (settings.RUN_STATE['in_progress'],
                                 settings.RUN_STATE['done'])]
        for run in runs:
            reserved_ram += run.used_ram
        return reserved_ram

    @property
    def used_disk(self):
        reserved_disk = 0

        runs = [run for run in self.runs
                if int(run.state) in (settings.RUN_STATE['in_progress'],
                                 settings.RUN_STATE['done'])]
        for run in runs:
            reserved_disk += run.used_disk
        return reserved_disk

    def add_env_to_server(self, run):
        run.server_id = self.id
        self.cur_tasks += 1

    def destroy_env(self):
        # TODO(implement and use)
        self.cur_tasks -= 1

    def erase_env(self, run):
        self.cur_tasks -= 1
        run.state = settings.RUN_STATE['removed']
        ext.db.session.commit()


class Task(ext.db.Model):
    id = ext.db.Column(ext.db.Integer, primary_key=True)
    name = ext.db.Column(ext.db.String(15), index=True, unique=True)
    desc = ext.db.Column(ext.db.String(150))
    taskfile = ext.db.Column(ext.db.String(150))
    taskname = ext.db.Column(ext.db.String(15), unique=True)
    state = ext.db.Column(ext.db.SmallInteger,
                          default=settings.TASK_STATE['on'])
    runs = ext.db.relationship('Run', backref='task', lazy='dynamic')

    def __repr__(self):
        return '<Task {0}>'.format(self.name)


class Run(ext.db.Model):
    id = ext.db.Column(ext.db.Integer, primary_key=True)
    state = ext.db.Column(ext.db.String(15),
                          default=settings.RUN_STATE['in_queue'])
    cmd_out = ext.db.Column(ext.db.Text(length=1048576), default=None)
    task_id = ext.db.Column(ext.db.Integer, ext.db.ForeignKey('task.id'))
    server_id = ext.db.Column(ext.db.Integer, ext.db.ForeignKey('server.id'),
                              default=None)
    user_id = ext.db.Column(ext.db.Integer, ext.db.ForeignKey('user.id'))
    end_datetime = ext.db.Column(ext.db.DateTime, default=None)
    start_datetime = ext.db.Column(ext.db.DateTime)
    # TODO(hop): to get rid of PickleType
    args = ext.db.Column(ext.db.PickleType, default=None)

    @property
    def used_ram(self):
        if (self.args and 'slave_node_cpu' in self.args and
                'nodes_count' in self.args):
            return self.args['slave_node_memory'] * self.args['nodes_count']
        return 0

    @property
    def used_disk(self):
        # TODO(used_disk): add parameter for disk and then implement
        return 100
