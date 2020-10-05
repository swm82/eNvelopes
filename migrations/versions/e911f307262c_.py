"""empty message

Revision ID: e911f307262c
Revises: 7d9a9dd65c2c
Create Date: 2020-10-04 22:22:44.799029

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e911f307262c'
down_revision = '7d9a9dd65c2c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('payees', schema=None) as batch_op:
        batch_op.create_foreign_key(batch_op.f('fk_payees_user_id_users'), 'users', ['user_id'], ['id'])

    with op.batch_alter_table('roles', schema=None) as batch_op:
        batch_op.create_unique_constraint(batch_op.f('uq_roles_name'), ['name'])

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_unique_constraint(batch_op.f('uq_users_email'), ['email'])
        batch_op.create_unique_constraint(batch_op.f('uq_users_username'), ['username'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_users_username'), type_='unique')
        batch_op.drop_constraint(batch_op.f('uq_users_email'), type_='unique')

    with op.batch_alter_table('roles', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_roles_name'), type_='unique')

    with op.batch_alter_table('payees', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_payees_user_id_users'), type_='foreignkey')

    # ### end Alembic commands ###