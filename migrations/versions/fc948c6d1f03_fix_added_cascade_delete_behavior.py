"""FIX: ADDED CASCADE DELETE BEHAVIOR

Revision ID: fc948c6d1f03
Revises: fc69168ec48d
Create Date: 2025-07-09 23:22:57.473650

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fc948c6d1f03'
down_revision = 'fc69168ec48d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('jobs', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('jobs_client_id_fkey'), type_='foreignkey')
        batch_op.create_foreign_key(None, 'users', ['client_id'], ['id'], ondelete='CASCADE')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('jobs', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(batch_op.f('jobs_client_id_fkey'), 'users', ['client_id'], ['id'])

    # ### end Alembic commands ###
