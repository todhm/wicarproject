"""make more info to save in owner send table

Revision ID: 647c9beb17b5
Revises: a770e2c66212
Create Date: 2018-05-18 13:10:32.515367

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '647c9beb17b5'
down_revision = 'a770e2c66212'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('owner_send', sa.Column('account_holder_name', sa.String(length=128), nullable=True))
    op.add_column('owner_send', sa.Column('account_num', sa.String(length=128), nullable=True))
    op.add_column('owner_send', sa.Column('account_num_masked', sa.String(length=128), nullable=True))
    op.add_column('owner_send', sa.Column('bank_name', sa.String(length=128), nullable=True))
    op.add_column('owner_send', sa.Column('bank_tran_date', sa.String(length=128), nullable=True))
    op.add_column('owner_send', sa.Column('print_content', sa.String(length=128), nullable=True))
    op.add_column('owner_send', sa.Column('register_date', sa.DateTime(), nullable=True))
    op.add_column('owner_send', sa.Column('wd_account_holder_name', sa.String(length=128), nullable=True))
    op.add_column('owner_send', sa.Column('wd_bank_name', sa.String(length=128), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('owner_send', 'wd_bank_name')
    op.drop_column('owner_send', 'wd_account_holder_name')
    op.drop_column('owner_send', 'register_date')
    op.drop_column('owner_send', 'print_content')
    op.drop_column('owner_send', 'bank_tran_date')
    op.drop_column('owner_send', 'bank_name')
    op.drop_column('owner_send', 'account_num_masked')
    op.drop_column('owner_send', 'account_num')
    op.drop_column('owner_send', 'account_holder_name')
    # ### end Alembic commands ###
