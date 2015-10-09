"""add index for tx_sn_stack.sn

Revision ID: 105686e049b1
Revises: 434198cbc796
Create Date: 2015-10-10 01:35:58.767910

"""

# revision identifiers, used by Alembic.
revision = '105686e049b1'
down_revision = '434198cbc796'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_index(op.f('ix_transaction_sn_stack_sn'), 'transaction_sn_stack', ['sn'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_transaction_sn_stack_sn'), table_name='transaction_sn_stack')
