"""<message>

Revision ID: cee46b0bf8e0
Revises: 64560df70ed7
Create Date: 2023-06-13 00:20:00.234365

"""
import uuid

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "cee46b0bf8e0"
down_revision = "64560df70ed7"
branch_labels = None
depends_on = None


def gen_id() -> str:
    return str(uuid.uuid4())


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    order_type = op.create_table(
        "order_type",
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
    conn = op.get_bind()
    order_types = [
        {"id": gen_id(), "name": "Заказ на баню"},
        {"id": gen_id(), "name": "Заявка на сруб"},
        {"id": gen_id(), "name": "Заявка на брак сруба"},
    ]
    op.bulk_insert(order_type, order_types)

    op.create_index(op.f("ix_order_type_id"), "order_type", ["id"], unique=False)
    op.create_table(
        "order",
        sa.Column("status", sa.String(length=100), nullable=True),
        sa.Column("user_customer", sa.String(length=100), nullable=True),
        sa.Column("user_implementer", sa.String(length=100), nullable=True),
        sa.Column("order_type_id", sa.String(length=50), nullable=True),
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
            ["order_type_id"],
            ["order_type.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_order_id"), "order", ["id"], unique=False)
    order_type_param = op.create_table(
        "order_type_param",
        sa.Column("name", sa.String(length=100), nullable=True),
        sa.Column("value_type", sa.String(length=100), nullable=True),
        sa.Column("required", sa.Boolean(), nullable=True),
        sa.Column("order_type_id", sa.String(length=50), nullable=True),
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
            ["order_type_id"],
            ["order_type.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    order_type_params = [
        {
            "id": gen_id(),
            "name": "Название",
            "required": True,
            "order_type_id": order_types[0]["id"],
            "value_type": "string",
        },
        {
            "id": gen_id(),
            "name": "Описание",
            "required": True,
            "order_type_id": order_types[0]["id"],
            "value_type": "string",
        },
        {
            "id": gen_id(),
            "name": "Бюджет",
            "required": True,
            "order_type_id": order_types[0]["id"],
            "value_type": "int",
        },
        {
            "id": gen_id(),
            "name": "Название",
            "required": True,
            "order_type_id": order_types[1]["id"],
            "value_type": "string",
        },
        {
            "id": gen_id(),
            "name": "Описание",
            "required": False,
            "order_type_id": order_types[1]["id"],
            "value_type": "string",
        },
        {
            "id": gen_id(),
            "name": "Объем девесины, м3",
            "required": True,
            "order_type_id": order_types[1]["id"],
            "value_type": "int",
        },
        {
            "id": gen_id(),
            "name": "Срок исполнения",
            "required": True,
            "order_type_id": order_types[1]["id"],
            "value_type": "date",
        },
        {
            "id": gen_id(),
            "name": "Причина отказа",
            "required": True,
            "order_type_id": order_types[2]["id"],
            "value_type": "string",
        },
    ]
    op.bulk_insert(order_type_param, order_type_params)
    op.create_index(
        op.f("ix_order_type_param_id"), "order_type_param", ["id"], unique=False
    )
    op.create_table(
        "order_confirmation",
        sa.Column("user", sa.String(length=100), nullable=True),
        sa.Column("signed", sa.Boolean(), nullable=True),
        sa.Column("order_id", sa.String(length=50), nullable=True),
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
            ["order_id"],
            ["order.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_order_confirmation_id"), "order_confirmation", ["id"], unique=False
    )
    op.create_table(
        "order_param_value",
        sa.Column("value", sa.String(length=100), nullable=True),
        sa.Column("order_type_param_id", sa.String(length=50), nullable=True),
        sa.Column("order_id", sa.String(length=50), nullable=True),
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
            ["order_id"],
            ["order.id"],
        ),
        sa.ForeignKeyConstraint(
            ["order_type_param_id"],
            ["order_type_param.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_order_param_value_id"), "order_param_value", ["id"], unique=False
    )
    op.drop_index("ix_task_id", table_name="task")
    op.drop_table("task")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "task",
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column("id", sa.VARCHAR(length=36), autoincrement=False, nullable=False),
        sa.Column(
            "content", sa.VARCHAR(length=100), autoincrement=False, nullable=True
        ),
        sa.PrimaryKeyConstraint("id", name="task_pkey"),
    )
    op.create_index("ix_task_id", "task", ["id"], unique=False)
    op.drop_index(op.f("ix_order_param_value_id"), table_name="order_param_value")
    op.drop_table("order_param_value")
    op.drop_index(op.f("ix_order_confirmation_id"), table_name="order_confirmation")
    op.drop_table("order_confirmation")
    op.drop_index(op.f("ix_order_type_param_id"), table_name="order_type_param")
    op.drop_table("order_type_param")
    op.drop_index(op.f("ix_order_id"), table_name="order")
    op.drop_table("order")
    op.drop_index(op.f("ix_order_type_id"), table_name="order_type")
    op.drop_table("order_type")
    # ### end Alembic commands ###
