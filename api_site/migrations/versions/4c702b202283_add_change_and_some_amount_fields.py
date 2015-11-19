"""add change and some amount fields.

Revision ID: 4c702b202283
Revises: 4c8dbc7297f3
Create Date: 2015-11-17 16:21:09.255994

"""

# revision identifiers, used by Alembic.
revision = '4c702b202283'
down_revision = '4c8dbc7297f3'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('payment_record', sa.Column('paid_amount', sa.Numeric(precision=16, scale=2), nullable=False, info={'after': 'amount'}))
    op.add_column('payment_record', sa.Column('real_amount', sa.Numeric(precision=16, scale=2), nullable=False, info={'after': 'amount'}))
    op.add_column('transaction_sn_stack', sa.Column('change', sa.Enum(u'EXPIRED', u'AMOUNT', u'INFO'), nullable=True, info={'after': 'state'}))


def downgrade():
    op.drop_column('transaction_sn_stack', 'change')
    op.drop_column('payment_record', 'real_amount')
    op.drop_column('payment_record', 'paid_amount')
