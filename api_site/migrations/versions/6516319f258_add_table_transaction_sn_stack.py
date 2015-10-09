"""add table transaction_sn_stack.

Revision ID: 6516319f258
Revises: 2fd2df3f92cd
Create Date: 2015-10-10 00:52:00.395932

"""

# revision identifiers, used by Alembic.
revision = '6516319f258'
down_revision = '2fd2df3f92cd'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('transaction_sn_stack',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('tx_id', sa.BigInteger(), nullable=False),
    sa.Column('sn', sa.CHAR(length=32), nullable=True),
    sa.Column('generated_on', sa.DateTime(), nullable=False),
    sa.Column('state', sa.VARCHAR(length=32), nullable=False),
    sa.Column('pushed_on', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['tx_id'], ['transaction.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('transaction_sn_stack')
