"""add weixin relations to channel table.

Revision ID: 36aa04970206
Revises: 227feced4a95
Create Date: 2015-10-25 19:45:10.762596

"""

# revision identifiers, used by Alembic.
revision = '36aa04970206'
down_revision = '227feced4a95'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('channel', sa.Column('wx_main', sa.VARCHAR(length=32), nullable=True))
    op.add_column('channel', sa.Column('wx_app', sa.VARCHAR(length=32), nullable=True))


def downgrade():
    op.drop_column('channel', 'wx_app')
    op.drop_column('channel', 'wx_main')
