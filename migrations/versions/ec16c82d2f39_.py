"""empty message

Revision ID: d8fd899d2ee0
Revises: 45052bf142c5
Create Date: 2020-09-13 01:07:24.503302

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ec16c82df39'
down_revision = 'd8fd899d2ee0'
branch_labels = None
depends_on = None


def upgrade():
	pass
    # ### commands auto generated by Alembic - please adjust! ###
    #op.add_column('collections', sa.Column('designer', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('collections', 'designer')
    # ### end Alembic commands ###