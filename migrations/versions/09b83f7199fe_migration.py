"""migration

Revision ID: 09b83f7199fe
Revises: 
Create Date: 2023-03-17 22:36:51.421380

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '09b83f7199fe'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('password', sa.String(length=200), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.Column('profile_image', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('messages',
    sa.Column('message_id', sa.Integer(), nullable=False),
    sa.Column('reciever', sa.Integer(), nullable=True),
    sa.Column('sended_by', sa.Integer(), nullable=True),
    sa.Column('message', sa.String(length=1000), nullable=True),
    sa.Column('profile_image', sa.String(length=100), nullable=True),
    sa.ForeignKeyConstraint(['reciever'], ['users.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['sended_by'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('message_id')
    )
    op.create_table('rooms',
    sa.Column('room_id', sa.Integer(), nullable=False),
    sa.Column('room_name', sa.String(length=100), nullable=False),
    sa.Column('created_by', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
    sa.PrimaryKeyConstraint('room_id')
    )
    op.create_table('favorite_messages',
    sa.Column('favorite_id', sa.Integer(), nullable=False),
    sa.Column('favorite_message_id', sa.Integer(), nullable=False),
    sa.Column('favorite_by', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['favorite_by'], ['users.id'], ),
    sa.ForeignKeyConstraint(['favorite_message_id'], ['messages.message_id'], ),
    sa.PrimaryKeyConstraint('favorite_id')
    )
    op.create_table('room_messages',
    sa.Column('room_message_id', sa.Integer(), nullable=False),
    sa.Column('room_id', sa.Integer(), nullable=False),
    sa.Column('msg_by', sa.Integer(), nullable=False),
    sa.Column('message', sa.String(length=1000), nullable=True),
    sa.Column('profile_image', sa.String(length=100), nullable=True),
    sa.ForeignKeyConstraint(['msg_by'], ['users.id'], ),
    sa.ForeignKeyConstraint(['room_id'], ['rooms.room_id'], ),
    sa.PrimaryKeyConstraint('room_message_id')
    )
    op.create_table('room_favorite_messages',
    sa.Column('room_favorite_id', sa.Integer(), nullable=False),
    sa.Column('room_favorite_message_id', sa.Integer(), nullable=False),
    sa.Column('favorite_by', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['favorite_by'], ['users.id'], ),
    sa.ForeignKeyConstraint(['room_favorite_message_id'], ['room_messages.room_message_id'], ),
    sa.PrimaryKeyConstraint('room_favorite_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('room_favorite_messages')
    op.drop_table('room_messages')
    op.drop_table('favorite_messages')
    op.drop_table('rooms')
    op.drop_table('messages')
    op.drop_table('users')
    # ### end Alembic commands ###