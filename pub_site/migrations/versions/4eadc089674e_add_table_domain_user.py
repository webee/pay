"""add table domain_user.

Revision ID: 4eadc089674e
Revises: 59645a8811d3
Create Date: 2015-12-16 21:03:33.809708

"""

# revision identifiers, used by Alembic.
revision = '4eadc089674e'
down_revision = '59645a8811d3'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('domain_user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_domain_name', sa.VARCHAR(length=32), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('phone', sa.String(length=18), nullable=False),
    sa.Column('password', sa.String(length=128), nullable=True),
    sa.Column('created_on', sa.DateTime(), nullable=False),
    sa.Column('last_seen', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_domain_name', 'username', name='user_domain_user_name_uniq_idx')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('domain_user')
    ### end Alembic commands ###
