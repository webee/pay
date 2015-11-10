"""rm wx_main/app from channel.

Revision ID: 3d907575ba8e
Revises: 414d0ec3a32c
Create Date: 2015-11-10 14:59:34.519507

"""

# revision identifiers, used by Alembic.
revision = '3d907575ba8e'
down_revision = '414d0ec3a32c'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.drop_column('channel', 'wx_main')
    op.drop_column('channel', 'wx_app')


def downgrade():
    op.add_column('channel', sa.Column('wx_app', mysql.VARCHAR(length=32), nullable=True))
    op.add_column('channel', sa.Column('wx_main', mysql.VARCHAR(length=32), nullable=True))
