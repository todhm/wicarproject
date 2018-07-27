"""add car price schedule table

Revision ID: 86b8ecd7fa47
Revises: ca25708ef348
Create Date: 2018-06-14 14:35:21.222568

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '86b8ecd7fa47'
down_revision = 'ca25708ef348'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('car_price_schedule',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('car_id', sa.String(), nullable=True),
    sa.Column('start_time', sa.DateTime(), nullable=True),
    sa.Column('end_time', sa.DateTime(), nullable=True),
    sa.Column('price', sa.Integer(), nullable=True),
    sa.Column('register_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['car_id'], ['car.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_car_price_schedule_car_id'), 'car_price_schedule', ['car_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_car_price_schedule_car_id'), table_name='car_price_schedule')
    op.drop_table('car_price_schedule')
    # ### end Alembic commands ###
