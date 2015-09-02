"""make order_id not null and default empty.

Revision ID: 2fd2df3f92cd
Revises: 186976ecb20
Create Date: 2015-09-02 16:47:59.592089

"""

# revision identifiers, used by Alembic.
revision = '2fd2df3f92cd'
down_revision = '186976ecb20'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.alter_column('transaction', 'order_id',
               existing_type=mysql.VARCHAR(length=64),
               nullable=False)


def downgrade():
    op.alter_column('transaction', 'order_id',
               existing_type=mysql.VARCHAR(length=64),
               nullable=True)
