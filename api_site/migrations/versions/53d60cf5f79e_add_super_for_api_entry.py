"""add super for api_entry.

Revision ID: 53d60cf5f79e
Revises: c7d9901e405
Create Date: 2015-11-26 16:56:41.711253

"""

# revision identifiers, used by Alembic.
revision = '53d60cf5f79e'
down_revision = 'c7d9901e405'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('api_entry', sa.Column('super_id', sa.Integer(), nullable=True, info={'after': 'id'}))
    op.create_foreign_key('fk_api_entry_super_id_api_entry', 'api_entry', 'api_entry', ['super_id'], ['id'])


def downgrade():
    op.drop_constraint('fk_api_entry_super_id_api_entry', 'api_entry', type_='foreignkey')
    op.drop_column('api_entry', 'super_id')
