"""rename defect order 2

Revision ID: db91372fb7f3
Revises: 6534e44e3ddc
Create Date: 2023-06-21 18:02:52.950679

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'db91372fb7f3'
down_revision = '6534e44e3ddc'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    order_dep_types = [
        {'name': 'Заявка на брак', 'dep_type': 'DEFECT'},
    ]
    bind = op.get_bind()
    for it in order_dep_types:
        op.execute(f'UPDATE order_type SET name = \'{it["name"]}\' WHERE dep_type LIKE \'{it["dep_type"]}\'')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###