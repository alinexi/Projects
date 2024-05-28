"""Add salary and tax percentage to User model

Revision ID: 6893ac6eb454
Revises: 73e2b7361327
Create Date: 2024-05-29 00:47:55.131156

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6893ac6eb454'
down_revision = '73e2b7361327'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('salary', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('tax_percentage', sa.Float(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('tax_percentage')
        batch_op.drop_column('salary')

    # ### end Alembic commands ###