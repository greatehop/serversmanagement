import settings

from flask.ext.wtf import Form
from app import models
from wtforms import TextField, SelectField, IntegerField, \
                    BooleanField, HiddenField
from wtforms.validators import Required, IPAddress, NumberRange, \
                               ValidationError


class UniqueValidator(object):
    """
    validator that checks field uniqueness
    """

    def __init__(self, model, field, message=None):
        self.model = model
        self.field = field
        if not message:
            message = 'The element already exists!'
        self.message = message

    def __call__(self, form, field):
        existing = self.model.query.filter(self.field==field.data).first()
        try:
            id = int(form.id.data)
        except:
            id = None
        if existing and (id is None or id != existing.id):
            raise ValidationError(self.message)

class LoginForm(Form): pass

class ServerForm(Form):
    id = HiddenField('id')
    ip = TextField('ip',
        validators=[IPAddress(), UniqueValidator(
            models.Server, models.Server.ip,
            'There is already server with that IP')])
    alias = TextField('alias',
        validators=[Required(), UniqueValidator(
            models.Server, models.Server.alias,
            'There is already server with that alias')])
    is_active = BooleanField('is_active', default=True)
    max_tasks = IntegerField('max_tasks',
                             default=settings.MAX_TASKS,
                             validators=[NumberRange(min=1)])

class UserForm(Form):
    is_admin = BooleanField('is_admin', default=False)
    is_active = BooleanField('is_active', default=True)

class TaskDeployMOSForm(Form):
    #TODO: add unique validator
    deploy_name = TextField('deploy_name', validators=[Required()])
    iso_url = TextField('iso_url', validators=[Required()])
    node_count = IntegerField('node_count',
                              default=settings.NODE_COUNT,
                              validators=[NumberRange(min=1)])

    slave_node_cpu = SelectField('slave_node_cpu',
                                 validators=[],
                                 choices=[('1', '1'),
                                          ('2', '2'),
                                          ('4', '4')],
                                 default='1')
    slave_node_mem = SelectField('slave_node_mem',
                                 validators=[],
                                 choices=[('4096', '4096'),
                                          ('3072', '3072'),
                                          ('6144', '6144'),
                                          ('8192', '8192')],
                                 default='4096')
    keep_days = IntegerField('keep_days',
                             default=settings.KEEP_DAYS,
                             validators=[NumberRange(min=1)])

class TaskCleanMOSForm(Form):
    deploy_name = SelectField('deploy_name', coerce=int)

#TODO: taskform for admin user ?