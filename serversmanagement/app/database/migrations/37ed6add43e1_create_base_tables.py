"""create base tables

Revision ID: 37ed6add43e1
Revises:
Create Date: 2016-07-13 12:33:30.339925

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import orm

from serversmanagement.app.database import models
from serversmanagement import settings

# revision identifiers, used by Alembic.
revision = '37ed6add43e1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    op.create_table(
        'user',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(64), index=True, unique=True),
        sa.Column('role', sa.SmallInteger, default=settings.USER_ROLE['user']),
        sa.Column('email', sa.String(120), index=True, unique=True),
        sa.Column('state', sa.SmallInteger, default=settings.USER_STATE['on'])
    )

    op.create_table(
        'server',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('ip', sa.String(15), index=True, unique=True),
        sa.Column('alias', sa.String(120), index=True),
        sa.Column('state', sa.SmallInteger,
                  default=settings.SERVER_STATE['on']),
        sa.Column('max_tasks', sa.Integer, default=settings.MAX_TASKS),
        sa.Column('cur_tasks', sa.Integer, default=0)
    )

    op.create_table(
        'task',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(15), index=True, unique=True),
        sa.Column('desc', sa.String(150)),
        sa.Column('taskfile', sa.String(150)),
        sa.Column('taskname', sa.String(15), unique=True),
        sa.Column('state', sa.SmallInteger, default=settings.TASK_STATE['on'])
    )

    op.create_table(
        'run',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('state', sa.String(15),
                  default=settings.RUN_STATE['in_queue']),
        sa.Column('cmd_out', sa.Text(length=1048576), default=None),
        sa.Column('task_id', sa.Integer, sa.ForeignKey('task.id')),
        sa.Column('server_id', sa.Integer, sa.ForeignKey('server.id'),
                  default=None),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id')),
        sa.Column('end_datetime', sa.DateTime, default=None),
        sa.Column('start_datetime', sa.DateTime),
        # TODO(hop): to get rid of PickleType
        sa.Column('args', sa.PickleType, default=None)
    )
    task_deploy_mos = models.Task(name='deploy_mos',
                                  taskfile='./app/fabfile.py',
                                  taskname='deploy_mos')
    task_clean_mos = models.Task(name='clean_mos',
                                 taskfile='./app/fabfile.py',
                                 taskname='clean_mos')
    session.add(task_deploy_mos)
    session.add(task_clean_mos)
    session.commit()


def downgrade():
    op.drop_table('run')
    op.drop_table('task')
    op.drop_table('server')
    op.drop_table('user')
