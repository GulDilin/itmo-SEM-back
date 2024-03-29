"""order links

Revision ID: 390693bb4863
Revises: cee46b0bf8e0
Create Date: 2023-06-14 02:21:57.686968

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "390693bb4863"
down_revision = "cee46b0bf8e0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    order_link_type = op.create_table(
        "order_link_type",
        sa.Column("name", sa.String(length=100), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_order_link_type_id"), "order_link_type", ["id"], unique=False
    )

    conn = op.get_bind()
    op.bulk_insert(
        order_link_type,
        [
            {"id": "1", "name": "Заявка"},
            {"id": "2", "name": "Заявка на брак"},
        ],
    )

    op.create_table(
        "order_link",
        sa.Column("order_left_id", sa.String(length=50), nullable=False),
        sa.Column("order_right_id", sa.String(length=50), nullable=False),
        sa.Column("link_type_id", sa.String(length=50), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["link_type_id"],
            ["order_link_type.id"],
        ),
        sa.ForeignKeyConstraint(
            ["order_left_id"],
            ["order.id"],
        ),
        sa.ForeignKeyConstraint(
            ["order_right_id"],
            ["order.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_order_link_id"), "order_link", ["id"], unique=False)
    op.alter_column(
        "order", "order_type_id", existing_type=sa.VARCHAR(length=50), nullable=False
    )
    op.alter_column(
        "order_confirmation",
        "order_id",
        existing_type=sa.VARCHAR(length=50),
        nullable=False,
    )
    op.alter_column(
        "order_param_value",
        "order_type_param_id",
        existing_type=sa.VARCHAR(length=50),
        nullable=False,
    )
    op.alter_column(
        "order_param_value",
        "order_id",
        existing_type=sa.VARCHAR(length=50),
        nullable=False,
    )
    op.alter_column(
        "order_type_param",
        "order_type_id",
        existing_type=sa.VARCHAR(length=50),
        nullable=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "order_type_param",
        "order_type_id",
        existing_type=sa.VARCHAR(length=50),
        nullable=True,
    )
    op.alter_column(
        "order_param_value",
        "order_id",
        existing_type=sa.VARCHAR(length=50),
        nullable=True,
    )
    op.alter_column(
        "order_param_value",
        "order_type_param_id",
        existing_type=sa.VARCHAR(length=50),
        nullable=True,
    )
    op.alter_column(
        "order_confirmation",
        "order_id",
        existing_type=sa.VARCHAR(length=50),
        nullable=True,
    )
    op.alter_column(
        "order", "order_type_id", existing_type=sa.VARCHAR(length=50), nullable=True
    )
    op.drop_index(op.f("ix_order_link_id"), table_name="order_link")
    op.drop_table("order_link")
    op.drop_index(op.f("ix_order_link_type_id"), table_name="order_link_type")
    op.drop_table("order_link_type")
    # ### end Alembic commands ###
