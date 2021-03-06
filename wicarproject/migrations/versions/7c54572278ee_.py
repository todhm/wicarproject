"""empty message

Revision ID: 7c54572278ee
Revises: 05a6cb49bf3f
Create Date: 2018-05-14 13:36:55.910673

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7c54572278ee'
down_revision = '05a6cb49bf3f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('car_booking', sa.Column('total_distance', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('car_booking', 'total_distance')
    # ### end Alembic commands ###
