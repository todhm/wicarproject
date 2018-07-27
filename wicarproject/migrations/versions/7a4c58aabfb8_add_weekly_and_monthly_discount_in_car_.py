"""add weekly and monthly discount in car option 

Revision ID: 7a4c58aabfb8
Revises: 86b8ecd7fa47
Create Date: 2018-06-15 14:59:30.084362

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7a4c58aabfb8'
down_revision = '86b8ecd7fa47'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('car_option', sa.Column('monthly_discount', sa.Integer(), nullable=True))
    op.add_column('car_option', sa.Column('weekly_discount', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('car_option', 'weekly_discount')
    op.drop_column('car_option', 'monthly_discount')
    # ### end Alembic commands ###
