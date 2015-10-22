"""add super_id in transaction table to represent tx super/sub relations.

Revision ID: 227feced4a95
Revises: 20b33b1e95ac
Create Date: 2015-10-22 16:19:49.267678

"""

# revision identifiers, used by Alembic.
revision = '227feced4a95'
down_revision = '20b33b1e95ac'


from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('transaction', sa.Column('super_id', sa.BigInteger(), nullable=True, info={'after': 'id'}))
    op.create_foreign_key(None, 'transaction', 'transaction', ['super_id'], ['id'])


def downgrade():
    op.drop_constraint(None, 'transaction', type_='foreignkey')
    op.drop_column('transaction', 'super_id')
