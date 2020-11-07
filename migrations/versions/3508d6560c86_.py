"""empty message

Revision ID: 3508d6560c86
Revises: 
Create Date: 2020-11-03 09:16:46.151280

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '3508d6560c86'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('username', table_name='user_data')
    op.drop_table('user_data')
    op.drop_column('users', 'phone')
    op.drop_column('users', 'age')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('age', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.add_column('users', sa.Column('phone', mysql.VARCHAR(length=11), nullable=True))
    op.create_table('user_data',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('username', mysql.VARCHAR(length=16), nullable=False),
    sa.Column('list', mysql.TEXT(), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['users.id'], name='user_data_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('username', 'user_data', ['username'], unique=True)
    # ### end Alembic commands ###
