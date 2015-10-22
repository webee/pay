"""add group_id for transaction_state_log.

Revision ID: 20b33b1e95ac
Revises: 105686e049b1
Create Date: 2015-10-20 23:05:47.923283

"""

# revision identifiers, used by Alembic.
revision = '20b33b1e95ac'
down_revision = '105686e049b1'


from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('transaction_state_log', sa.Column('group_id', sa.BigInteger(), nullable=False, info={'after': 'id'}))


def downgrade():
    op.drop_column('transaction_state_log', 'group_id')
