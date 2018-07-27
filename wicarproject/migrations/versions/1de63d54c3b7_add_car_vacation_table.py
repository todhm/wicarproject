"""add car vacation table

Revision ID: 1de63d54c3b7
Revises: 7a4c58aabfb8
Create Date: 2018-06-18 09:04:12.956727

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1de63d54c3b7'
down_revision = '7a4c58aabfb8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('car_vacation',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('car_id', sa.String(), nullable=True),
    sa.Column('start_time', sa.DateTime(), nullable=True),
    sa.Column('end_time', sa.DateTime(), nullable=True),
    sa.Column('register_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['car_id'], ['car.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_car_vacation_car_id'), 'car_vacation', ['car_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_car_vacation_car_id'), table_name='car_vacation')
    op.drop_table('car_vacation')
    # ### end Alembic commands ###
