import config
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64), index = True, unique = True)
    role = db.Column(db.SmallInteger, default=config.USER_ROLE['user'])
    email = db.Column(db.String(120), index = True, unique = True)
    #TODO: to get rid of PickleType
    attributes = db.Column(db.PickleType)
    state = db.Column(db.SmallInteger, default=config.USER_STATE['on'])
    runs = db.relationship('Run', backref = 'user', lazy = 'dynamic')
    
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id) # python 2
        except NameError:
            return str(self.id) # python 3
        
    def __repr__(self):
        return '<User %r>' % (self.name)

class Server(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    ip = db.Column(db.String(15), index = True, unique = True)
    alias = db.Column(db.String(120), index = True)
    state = db.Column(db.SmallInteger, default=config.SERVER_STATE['on'])
    #TODO: to get rid of PickleType
    attributes = db.Column(db.PickleType)
    runs = db.relationship('Run', backref = 'server', lazy = 'dynamic')
    #TODO: add user/pass (user default=config.ssh_user), ssh_port default=22

    def __repr__(self):
        return '<Server %r>' % (self.alias)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(15), index = True, unique = True)
    desc = db.Column(db.String(120), index = True)
    taskfile = db.Column(db.String(15), index = True)
    taskname = db.Column(db.String(15), index = True, unique = True)
    state = db.Column(db.SmallInteger, default=config.TASK_STATE['on'])
    runs = db.relationship('Run', backref = 'task', lazy = 'dynamic')
    
    def __repr__(self):
        return '<Task %r>' % (self.taskname)
     
class Run(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    state = db.Column(db.String(15))
    attributes = db.Column(db.PickleType)
    datetime = db.Column(db.DateTime)
    cmd_out = db.Column(db.Text)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    server_id = db.Column(db.Integer, db.ForeignKey('server.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    #TODO: duration???
