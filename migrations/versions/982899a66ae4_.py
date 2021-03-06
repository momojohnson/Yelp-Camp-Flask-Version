"""empty message

Revision ID: 982899a66ae4
Revises: 665a24b0ed37
Create Date: 2018-06-03 22:04:43.957341

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '982899a66ae4'
down_revision = '665a24b0ed37'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('campgrounds', sa.Column('image_id', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('campgrounds', 'image_id')
    # ### end Alembic commands ###
