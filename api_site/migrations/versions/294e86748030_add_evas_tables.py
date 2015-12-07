"""add evas tables.

Revision ID: 294e86748030
Revises: 35d697f6f33d
Create Date: 2015-12-07 16:21:49.631455

"""

# revision identifiers, used by Alembic.
revision = '294e86748030'
down_revision = '35d697f6f33d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('evas_alipay_batch_refund_record',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('batch_no', sa.CHAR(length=32), nullable=False),
    sa.Column('refund_tx_sn', sa.CHAR(length=32), nullable=False),
    sa.Column('created_on', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('refund_tx_sn')
    )
    op.create_table('evas_notify_log',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('vas_name', sa.VARCHAR(length=32), nullable=False),
    sa.Column('event', sa.VARCHAR(length=32), nullable=False),
    sa.Column('content', sa.UnicodeText(), nullable=True),
    sa.Column('created_on', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('evas_notify_log')
    op.drop_table('evas_alipay_batch_refund_record')
