"""change cheque record add required_at

Revision ID: 488e5030eb8c
Revises: 1a09d3c6f84d
Create Date: 2016-01-23 00:22:54.841663

"""

# revision identifiers, used by Alembic.
revision = '488e5030eb8c'
down_revision = '1a09d3c6f84d'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('cheque_record', sa.Column('expired_at', sa.DateTime(), nullable=False))
    op.drop_column('cheque_record', 'valid_minutes')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('cheque_record', sa.Column('valid_minutes', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False))
    op.drop_column('cheque_record', 'expired_at')
    ### end Alembic commands ###
