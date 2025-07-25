"""Add sentiment field to Job model

Revision ID: 7ff6a7d9affb
Revises: 35caa6a45075
Create Date: 2025-06-30 11:49:15.694675

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7ff6a7d9affb'
down_revision = '35caa6a45075'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('jobs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('sentiment', sa.String(length=50), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('jobs', schema=None) as batch_op:
        batch_op.drop_column('sentiment')

    # ### end Alembic commands ###
