import datetime
import config
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64), index = True, unique = True)
    role = db.Column(db.SmallInteger, default=config.user_role['user'])
    email = db.Column(db.String(120), index = True, unique = True)
    attributes = db.Column(db.PickleType)
    state = db.Column(db.SmallInteger, default=config.user_state['on'])
    #runs = db.relationship('Run', backref = 'user', lazy = 'dynamic')
    
    def __repr__(self):
        return '<User %r>' % (self.username)

class Server(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    ip = db.Column(db.String(15), index = True, unique = True)
    alias = db.Column(db.String(120), index = True, unique = False)
    state = db.Column(db.SmallInteger, default=config.server_state['on'])
    attributes = db.Column(db.PickleType)
    runs = db.relationship('Run', backref = 'server', lazy = 'dynamic')
    #TODO: add user/pass (user default=config.ssh_user), ssh_port default=22

class Task(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(15), index = True, unique = True)
    desc = db.Column(db.String(120), index = True, unique = False)
    taskfile = db.Column(db.String(15), index = True, unique = False)
    taskname = db.Column(db.String(15), index = True, unique = True)
    state = db.Column(db.SmallInteger, default=config.task_state['on'])
    runs = db.relationship('Run', backref = 'task', lazy = 'dynamic')
    
    def __repr__(self):
        return '<Task %r>' % (self.taskname)

    """
    def update_state(self, new_state):
        self.state = new_state
    """
     
class Run(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    state = db.Column(db.String(15))
    attributes = db.Column(db.PickleType)
    datetime = db.Column(db.DateTime)
    cmd_out = db.Column(db.Text)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    server_id = db.Column(db.Integer, db.ForeignKey('server.id'))
    #user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    #TODO: duration???

    def __init__(self, state, task_id, attributes, server_id=None, cmd_out=None):
        self.state = state
        self.task_id = task_id
        self.attributes = attributes
        self.datetime = datetime.datetime.utcnow()
        if server_id is not None:
            self.server_id = server_id
        if cmd_out is not None:
            self.cmd_out = cmd_out
