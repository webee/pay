"""update api_entry add value field.

Revision ID: 35d697f6f33d
Revises: 20d7fd1c8038
Create Date: 2015-11-30 00:38:52.177102

"""

# revision identifiers, used by Alembic.
revision = '35d697f6f33d'
down_revision = '20d7fd1c8038'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('api_entry', sa.Column('updated_on', sa.DateTime(), nullable=False))
    op.add_column('api_entry', sa.Column('value', sa.VARCHAR(length=256), nullable=True, info={'after': 'name'}))


def downgrade():
    op.drop_column('api_entry', 'value')
    op.drop_column('api_entry', 'updated_on')
