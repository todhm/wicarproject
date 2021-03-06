"""drop foreign key constraint of user and car id

Revision ID: 0e1fc0521c97
Revises: 8256c3fca5c5
Create Date: 2018-05-09 15:13:19.263053

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0e1fc0521c97'
down_revision = '8256c3fca5c5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('car_user_id_fkey', 'car', type_='foreignkey')
    op.drop_constraint('car_booking_car_id_fkey', 'car_booking', type_='foreignkey')
    op.drop_constraint('car_booking_renter_id_fkey', 'car_booking', type_='foreignkey')
    op.drop_constraint('car_image_car_id_fkey', 'car_image', type_='foreignkey')
    op.drop_constraint('car_option_id_fkey', 'car_option', type_='foreignkey')
    op.create_index(op.f('ix_message_receiver_id'), 'message', ['receiver_id'], unique=False)
    op.create_index(op.f('ix_message_sender_id'), 'message', ['sender_id'], unique=False)
    op.drop_constraint('message_receiver_id_fkey', 'message', type_='foreignkey')
    op.drop_constraint('message_sender_id_fkey', 'message', type_='foreignkey')
    op.create_index(op.f('ix_owner_review_owner_id'), 'owner_review', ['owner_id'], unique=False)
    op.drop_constraint('owner_review_owner_id_fkey', 'owner_review', type_='foreignkey')
    op.create_index(op.f('ix_renter_review_renter_id'), 'renter_review', ['renter_id'], unique=False)
    op.drop_constraint('renter_review_renter_id_fkey', 'renter_review', type_='foreignkey')
    op.drop_constraint('user_card_user_id_fkey', 'user_card', type_='foreignkey')
    op.drop_constraint('user_time_user_id_fkey', 'user_time', type_='foreignkey')
    op.drop_constraint('vacation_data_user_id_fkey', 'vacation_data', type_='foreignkey')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key('vacation_data_user_id_fkey', 'vacation_data', 'user', ['user_id'], ['id'])
    op.alter_column('vacation_data', 'user_id',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_nullable=True)
    op.create_foreign_key('user_time_user_id_fkey', 'user_time', 'user', ['user_id'], ['id'])
    op.alter_column('user_time', 'user_id',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_nullable=True)
    op.create_foreign_key('user_card_user_id_fkey', 'user_card', 'user', ['user_id'], ['id'])
    op.alter_column('user_card', 'user_id',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               nullable=False)
    op.alter_column('user_bank', 'user_id',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_nullable=False)
    op.alter_column('user', 'id',
               existing_type=sa.String(length=80),
               type_=sa.INTEGER())
    op.create_foreign_key('renter_review_renter_id_fkey', 'renter_review', 'user', ['renter_id'], ['id'])
    op.drop_index(op.f('ix_renter_review_renter_id'), table_name='renter_review')
    op.alter_column('renter_review', 'renter_id',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_nullable=True)
    op.create_foreign_key('owner_review_owner_id_fkey', 'owner_review', 'user', ['owner_id'], ['id'])
    op.drop_index(op.f('ix_owner_review_owner_id'), table_name='owner_review')
    op.alter_column('owner_review', 'owner_id',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_nullable=True)
    op.create_foreign_key('message_sender_id_fkey', 'message', 'user', ['sender_id'], ['id'])
    op.create_foreign_key('message_receiver_id_fkey', 'message', 'user', ['receiver_id'], ['id'])
    op.drop_index(op.f('ix_message_sender_id'), table_name='message')
    op.drop_index(op.f('ix_message_receiver_id'), table_name='message')
    op.alter_column('message', 'sender_id',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_nullable=True)
    op.alter_column('message', 'receiver_id',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_nullable=True)
    op.create_foreign_key('car_option_id_fkey', 'car_option', 'car', ['id'], ['id'])
    op.alter_column('car_option', 'id',
               existing_type=sa.String(),
               type_=sa.INTEGER())
    op.create_foreign_key('car_image_car_id_fkey', 'car_image', 'car', ['car_id'], ['id'])
    op.alter_column('car_image', 'car_id',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_nullable=True)
    op.create_foreign_key('car_booking_renter_id_fkey', 'car_booking', 'user', ['renter_id'], ['id'])
    op.create_foreign_key('car_booking_car_id_fkey', 'car_booking', 'car', ['car_id'], ['id'])
    op.alter_column('car_booking', 'renter_id',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_nullable=True)
    op.alter_column('car_booking', 'car_id',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_nullable=True)
    op.create_foreign_key('car_user_id_fkey', 'car', 'user', ['user_id'], ['id'])
    op.alter_column('car', 'user_id',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_nullable=True)
    op.alter_column('car', 'id',
               existing_type=sa.String(length=80),
               type_=sa.INTEGER(),
               existing_server_default=sa.text("nextval('car_id_seq'::regclass)"))
    # ### end Alembic commands ###
