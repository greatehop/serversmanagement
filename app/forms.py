import flask_wtf
import wtforms
from wtforms import validators

from app.database import models
import settings


class UniqueValidator(object):
    """validator that checks field uniqueness"""

    def __init__(self, model, field, message=None):
        self.model = model
        self.field = field
        if not message:
            message = 'The element already exists!'
        self.message = message

    def __call__(self, form, field):
        existing = self.model.query.filter(self.field == field.data).first()
        try:
            id = int(form.id.data)
        except Exception:
            id = None
        if existing and (id is None or id != existing.id):
            raise validators.ValidationError(self.message)


class LoginForm(flask_wtf.Form):
    pass


class ServerForm(flask_wtf.Form):
    id = wtforms.HiddenField('id')
    ip = wtforms.StringField(
        'ip', validators=[validators.IPAddress(),
                          UniqueValidator(
                          models.Server, models.Server.ip,
                          'There is already server with that IP')])
    alias = wtforms.StringField(
        'alias', validators=[validators.DataRequired(),
                             UniqueValidator(
                             models.Server, models.Server.alias,
                             'There is already server with that alias')])
    is_active = wtforms.BooleanField('is_active', default=True)
    max_tasks = wtforms.IntegerField('max_tasks',
                                     default=settings.MAX_TASKS,
                                     validators=[validators.NumberRange(min=1)]
                                     )


class UserForm(flask_wtf.Form):
    is_admin = wtforms.BooleanField('is_admin', default=False)
    is_active = wtforms.BooleanField('is_active', default=True)


class TaskDeployMOSForm(flask_wtf.Form):
    deploy_name = wtforms.StringField('deploy_name', validators=[])
    iso_url = wtforms.StringField(
        'iso_url',
        validators=[validators.DataRequired(),
                    validators.Regexp(message='Invalid iso or torrent',
                                      regex='^.*\.(iso|torrent)$')])

    nodes_count = wtforms.IntegerField(
        'nodes_count',
        default=settings.NODES_COUNT,
        validators=[validators.NumberRange(min=1, max=7)])

    slave_node_cpu = wtforms.SelectField('slave_node_cpu',
                                         validators=[],
                                         choices=[('1', '1'),
                                                  ('2', '2'),
                                                  ('4', '4')],
                                         default='1')
    slave_node_memory = wtforms.SelectField('slave_node_memory',
                                            validators=[],
                                            choices=[('4096', '4096'),
                                                     ('3072', '3072'),
                                                     ('6144', '6144'),
                                                     ('8192', '8192')],
                                            default='4096')
    keep_days = wtforms.IntegerField('keep_days',
                                     default=settings.KEEP_DAYS,
                                     validators=[validators.NumberRange(min=0)]
                                     )
    ironic_nodes_count = wtforms.IntegerField(
        'ironic', default=0,
        validators=[validators.NumberRange(min=0)])


class TaskCleanMOSForm(flask_wtf.Form):
    deploy_name = wtforms.SelectField('deploy_name', coerce=int)
