"""empty message

Revision ID: 764ba0492a75
Revises: 
Create Date: 2020-10-04 21:30:36.824023

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '764ba0492a75'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('payees', sa.Column('user_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'payees', 'users', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'payees', type_='foreignkey')
    op.drop_column('payees', 'user_id')
    # ### end Alembic commands ###
