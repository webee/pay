"""add uniq key for tx.sn

Revision ID: 434198cbc796
Revises: 6516319f258
Create Date: 2015-10-10 01:19:49.907881

"""

# revision identifiers, used by Alembic.
revision = '434198cbc796'
down_revision = '6516319f258'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_unique_constraint('uniq_tx_sn', 'transaction', ['sn'])


def downgrade():
    op.drop_constraint('uniq_tx_sn', 'transaction', type_='unique')
