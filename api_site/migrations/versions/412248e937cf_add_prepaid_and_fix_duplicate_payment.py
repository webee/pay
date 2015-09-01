"""add_prepaid_and_fix_duplicate_payment.

Revision ID: 412248e937cf
Revises: 3c161e36dc1f
Create Date: 2015-09-01 14:45:50.294345

"""

# revision identifiers, used by Alembic.
revision = '412248e937cf'
down_revision = '3c161e36dc1f'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.add_column('duplicated_payment_record', sa.Column('source', sa.Enum(u'PAYMENT', u'PREPAID'), nullable=False))
    op.add_column('duplicated_payment_record', sa.Column('status', sa.SmallInteger(), nullable=False))
    op.add_column('duplicated_payment_record', sa.Column('updated_on', sa.DateTime(), nullable=False))
    op.alter_column('duplicated_payment_record', 'event_id',
               existing_type=mysql.BIGINT(display_width=20),
               nullable=False)
    op.add_column('prepaid_record', sa.Column('to_id', sa.Integer(), nullable=False))
    op.drop_column('prepaid_record', 'to_user_id')


def downgrade():
    op.add_column('prepaid_record', sa.Column('to_user_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False))
    op.drop_column('prepaid_record', 'to_id')
    op.alter_column('duplicated_payment_record', 'event_id',
               existing_type=mysql.BIGINT(display_width=20),
               nullable=True)
    op.drop_column('duplicated_payment_record', 'updated_on')
    op.drop_column('duplicated_payment_record', 'status')
    op.drop_column('duplicated_payment_record', 'source')
