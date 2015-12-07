"""update evas alipay batchrefund record.

Revision ID: 499dbfdd807d
Revises: 294e86748030
Create Date: 2015-12-07 16:52:36.066491

"""

# revision identifiers, used by Alembic.
revision = '499dbfdd807d'
down_revision = '294e86748030'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('evas_alipay_batch_refund_record', sa.Column('trade_no', sa.CHAR(length=32), nullable=False, info={'after': 'batch_no'}))
    op.create_unique_constraint(u'batch_no_trade_no_uniq_idx', 'evas_alipay_batch_refund_record', ['batch_no', 'trade_no'])


def downgrade():
    op.drop_constraint(u'batch_no_trade_no_uniq_idx', 'evas_alipay_batch_refund_record', type_='unique')
    op.drop_column('evas_alipay_batch_refund_record', 'trade_no')
