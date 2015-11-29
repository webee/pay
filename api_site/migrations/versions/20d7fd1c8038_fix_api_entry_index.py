"""fix api entry index.

Revision ID: 20d7fd1c8038
Revises: 53d60cf5f79e
Create Date: 2015-11-28 10:59:00.768603

"""

# revision identifiers, used by Alembic.
revision = '20d7fd1c8038'
down_revision = '53d60cf5f79e'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_index(op.f('ix_api_entry_name'), 'api_entry', ['name'], unique=False)
    op.create_unique_constraint(u'super_id_name_uniq_idx', 'api_entry', ['super_id', 'name'])
    op.drop_index('name', table_name='api_entry')


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_index('name', 'api_entry', ['name'], unique=True)
    op.drop_constraint(u'super_id_name_uniq_idx', 'api_entry', type_='unique')
    op.drop_index(op.f('ix_api_entry_name'), table_name='api_entry')
    ### end Alembic commands ###
