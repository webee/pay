"""add tried_times to payment record.

Revision ID: 3c161e36dc1f
Revises: None
Create Date: 2015-08-31 14:34:43.307315

"""

# revision identifiers, used by Alembic.
revision = '3c161e36dc1f'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('payment_record', sa.Column('tried_times', sa.Integer(), nullable=False))


def downgrade():
    op.drop_column('payment_record', 'tried_times')
