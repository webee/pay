"""remove secured from payment_record.

Revision ID: 186976ecb20
Revises: 4b8a67db557e
Create Date: 2015-09-02 03:52:02.794525

"""

# revision identifiers, used by Alembic.
revision = '186976ecb20'
down_revision = '4b8a67db557e'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.drop_column('payment_record', 'secured')


def downgrade():
    op.add_column('payment_record', sa.Column('secured', mysql.TINYINT(display_width=1), autoincrement=False, nullable=False))
