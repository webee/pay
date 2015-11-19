"""add debit note tables.

Revision ID: 4c8dbc7297f3
Revises: 110fe9819a1c
Create Date: 2015-11-11 11:39:37.803208

"""

# revision identifiers, used by Alembic.
revision = '4c8dbc7297f3'
down_revision = '110fe9819a1c'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('debit_note_date',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('state', sa.Boolean(), nullable=False),
                    sa.Column('date', sa.DateTime(), nullable=False),
                    sa.Column('vas_name', sa.VARCHAR(length=32), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )

    op.create_table('debit_note_detail',
                    sa.Column('id', sa.BigInteger(), nullable=False),
                    sa.Column('sn', sa.CHAR(length=32), nullable=False),
                    sa.Column('vas_name', sa.VARCHAR(length=32), nullable=False),
                    sa.Column('amount', sa.Numeric(precision=16, scale=2), nullable=False),
                    sa.Column('order_id', sa.VARCHAR(length=64), nullable=False),
                    sa.Column('state', sa.Boolean(), nullable=False),
                    sa.Column('valid', sa.Boolean(), nullable=False),
                    sa.Column('type', sa.Enum(u'PAYMENT', u'REFUND'), nullable=False),
                    sa.Column('created_on', sa.DateTime(), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )


def downgrade():
    op.drop_table('debit_note_detail')
    op.drop_table('debit_note_date')
