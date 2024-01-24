"""add materials

Revision ID: 4af9d12196f5
Revises: db91372fb7f3
Create Date: 2024-01-24 15:53:56.571628

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '4af9d12196f5'
down_revision = 'db91372fb7f3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('material',
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.Column('amount', sa.Integer(), nullable=True),
    sa.Column('value_type', sa.String(length=100), nullable=True),
    sa.Column('item_price', sa.Integer(), nullable=True),
    sa.Column('user_creator', sa.String(length=100), nullable=True),
    sa.Column('user_updator', sa.String(length=100), nullable=True),
    sa.Column('order_id', sa.String(length=50), nullable=False),
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['order_id'], ['order.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_material_id'), 'material', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_material_id'), table_name='material')
    op.drop_table('material')
    # ### end Alembic commands ###