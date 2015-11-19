"""add origin to payment_record.

Revision ID: c7d9901e405
Revises: 4c702b202283
Create Date: 2015-11-19 19:29:40.364400

"""

# revision identifiers, used by Alembic.
revision = 'c7d9901e405'
down_revision = '4c702b202283'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('payment_record', sa.Column('origin', sa.VARCHAR(length=32), nullable=True, info={'after': 'order_id'}))
    op.create_unique_constraint('channel_order_id_origin_uniq_idx', 'payment_record', ['channel_id', 'order_id', 'origin'])
    op.drop_index('channel_order_id_uniq_idx', table_name='payment_record')


def downgrade():
    op.create_index('channel_order_id_uniq_idx', 'payment_record', ['channel_id', 'order_id'], unique=True)
    op.drop_constraint('channel_order_id_origin_uniq_idx', 'payment_record', type_='unique')
    op.drop_column('payment_record', 'origin')
