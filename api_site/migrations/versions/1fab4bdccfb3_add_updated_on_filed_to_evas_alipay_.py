"""add updated_on filed to evas_alipay_batch_refund_record.

Revision ID: 1fab4bdccfb3
Revises: 499dbfdd807d
Create Date: 2015-12-12 11:34:47.085916

"""

# revision identifiers, used by Alembic.
revision = '1fab4bdccfb3'
down_revision = '499dbfdd807d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('evas_alipay_batch_refund_record', sa.Column('updated_on', sa.DateTime(), nullable=False, info={'after': 'created_on'}))


def downgrade():
    op.drop_column('evas_alipay_batch_refund_record', 'updated_on')
