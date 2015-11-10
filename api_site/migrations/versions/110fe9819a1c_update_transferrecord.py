"""update TransferRecord.

Revision ID: 110fe9819a1c
Revises: 3d907575ba8e
Create Date: 2015-11-10 17:22:50.682602

"""

# revision identifiers, used by Alembic.
revision = '110fe9819a1c'
down_revision = '3d907575ba8e'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def upgrade():
    op.alter_column('transfer_record', 'from_user_id', new_column_name='from_id', existing_type=mysql.INTEGER(display_width=11), autoincrement=False, nullable=False)
    op.alter_column('transfer_record', 'to_user_id', new_column_name='to_id', existing_type=mysql.INTEGER(display_width=11), autoincrement=False, nullable=False)


def downgrade():
    op.alter_column('transfer_record', 'from_id', new_column_name='from_user_id', existing_type=mysql.INTEGER(display_width=11), autoincrement=False, nullable=False)
    op.alter_column('transfer_record', 'to_id', new_column_name='to_user_id', existing_type=mysql.INTEGER(display_width=11), autoincrement=False, nullable=False)
