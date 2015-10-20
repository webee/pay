"""add group_id for transaction_state_log.

Revision ID: 20b33b1e95ac
Revises: 105686e049b1
Create Date: 2015-10-20 23:05:47.923283

"""

# revision identifiers, used by Alembic.
revision = '20b33b1e95ac'
down_revision = '105686e049b1'


from sqlalchemy.ext.compiler import compiles
from alembic.ddl.base import AddColumn

# refer: https://groups.google.com/forum/#!topic/sqlalchemy-alembic/izYq2EMYotI
# ideally, the @compiles system would have some way of getting
# us the "existing" @compiles decorator, so this part is the
# hack
specs = AddColumn.__dict__.get('_compiler_dispatcher').specs
existing_dispatch = specs.get('mysql', specs['default'])

@compiles(AddColumn, "mysql")
def add_column(element, compiler, **kw):
    text = existing_dispatch(element, compiler, **kw)
    if "after" in element.column.info:
        text += " AFTER %s" % element.column.info['after']
    return text
#
# from alembic.migration import MigrationContext
# from alembic.operations import Operations
#
# ctx = MigrationContext.configure(dialect_name="mysql", opts={"as_sql": True})
# op = Operations(ctx)

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('transaction_state_log', sa.Column('group_id', sa.BigInteger(), nullable=False, info={'after': 'id'}))


def downgrade():
    op.drop_column('transaction_state_log', 'group_id')
