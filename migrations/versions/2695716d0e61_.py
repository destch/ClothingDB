"""empty message

Revision ID: 2695716d0e61
Revises: 21a1282a5a7d
Create Date: 2020-08-30 20:40:58.087244

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2695716d0e61'
down_revision = '21a1282a5a7d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('sellers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('item_id', sa.Integer(), nullable=True),
    sa.Column('site', sa.String(), nullable=True),
    sa.Column('size', sa.String(), nullable=True),
    sa.Column('price', sa.String(), nullable=True),
    sa.Column('link', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['item_id'], ['items.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('sellers')
    # ### end Alembic commands ###
