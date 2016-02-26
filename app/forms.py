from flask.ext.wtf import Form
from wtforms import TextField, SelectField, IntegerField, BooleanField
from wtforms.validators import Required

#TODO: add/check validators

class TaskDeployMOSForm(Form):
    deployment_name = TextField('deployment_name', validators = [Required()])
    iso_url = TextField('iso_url', validators = [Required()])
    node_count = IntegerField('node_count', validators = [Required()], default=6)
    slave_node_cpu = SelectField('slave_node_cpu', validators=[],
                                         choices=[('1', '1'),
                                                  ('2', '2'),
                                                  ('4', '4')],
                                         default='1')
    slave_node_mem = SelectField('slave_node_mem', validators=[],
                                         choices=[('4096', '4096'),
                                                  ('3072', '3072'),
                                                  ('6144', '6144'),
                                                  ('8192', '8192')],
                                         default='4096')
    keep_days = IntegerField('keep_days', validators = [Required()], default=1)
    
class TaskCleanMOSForm(Form):
    #TODO: generate alive mos env for current user
    #TODO: and all env for admin user
    deployment_name = TextField('deployment_name', validators = [Required()])
   
class ServerForm(Form):
    ip = TextField('ip', validators = [Required()])
    alias = TextField('alias', validators = [Required()])
    is_enabled = BooleanField('is_enabled', default = True)
    #TODO: arguments???
    
class UserForm(Form):
    usersname = TextField('ip', validators = [Required()])
    is_admin = BooleanField('is_admin', default = False)
    is_enabled = BooleanField('is_enabled', default = True)
    #TODO: arguments???

class LoginForm(Form):
    openid = TextField('openid', validators = [Required()])
    remember_me = BooleanField('remember_me', default = True)

#TODO: taskform for admin user ?    