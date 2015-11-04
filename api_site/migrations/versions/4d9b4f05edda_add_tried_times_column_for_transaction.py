"""add tried_times column for transaction.

Revision ID: 4d9b4f05edda
Revises: 36aa04970206
Create Date: 2015-11-04 13:08:39.342765

"""

# revision identifiers, used by Alembic.
revision = '4d9b4f05edda'
down_revision = '36aa04970206'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('transaction', sa.Column('tried_times', sa.Integer(), nullable=False, info={'after': 'vas_sn'}))


def downgrade():
    op.drop_column('transaction', 'tried_times')
