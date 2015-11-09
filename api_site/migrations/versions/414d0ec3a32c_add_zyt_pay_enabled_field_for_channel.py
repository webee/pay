"""add zyt_pay_enabled. field for channel.

Revision ID: 414d0ec3a32c
Revises: 4d9b4f05edda
Create Date: 2015-11-09 18:08:46.420228

"""

# revision identifiers, used by Alembic.
revision = '414d0ec3a32c'
down_revision = '4d9b4f05edda'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('channel', sa.Column('zyt_pay_enabled', sa.BOOLEAN(), nullable=False))


def downgrade():
    op.drop_column('channel', 'zyt_pay_enabled')
