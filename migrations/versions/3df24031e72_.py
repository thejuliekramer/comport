"""empty message

Revision ID: 3df24031e72
Revises: 529cc76baaa
Create Date: 2015-09-21 17:50:44.106378

"""

# revision identifiers, used by Alembic.
revision = '3df24031e72'
down_revision = '529cc76baaa'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('links',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('department_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('url', sa.String(length=2083), nullable=False),
    sa.Column('type', sa.String(length=255), nullable=False),
    sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('links')
    ### end Alembic commands ###
