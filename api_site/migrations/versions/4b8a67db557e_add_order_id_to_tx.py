"""add order_id to tx.

Revision ID: 4b8a67db557e
Revises: 3bf363900605
Create Date: 2015-09-02 02:13:44.367930

"""

# revision identifiers, used by Alembic.
revision = '4b8a67db557e'
down_revision = '3bf363900605'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('transaction', sa.Column('order_id', sa.VARCHAR(length=64), nullable=True))


def downgrade():
    op.drop_column('transaction', 'order_id')
