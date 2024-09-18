"""user extended

Revision ID: 5491ef71a937
Revises: e30f6720c2e4
Create Date: 2024-09-12 15:49:15.411089

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5491ef71a937"
down_revision: Union[str, None] = "e30f6720c2e4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "users", sa.Column("first_name", sa.String(length=50), nullable=True)
    )
    op.add_column(
        "users", sa.Column("last_name", sa.String(length=50), nullable=True)
    )
    op.add_column("users", sa.Column("role", sa.String(), nullable=False))
    op.add_column(
        "users",
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.add_column(
        "users",
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column(
            "last_activity_at", sa.DateTime(timezone=True), nullable=False
        ),
    )
    op.add_column("users", sa.Column("balance", sa.Integer(), nullable=False))
    op.add_column(
        "users", sa.Column("block_status", sa.Boolean(), nullable=False)
    )
    op.add_column(
        "users",
        sa.Column("block_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "users", sa.Column("is_deleted", sa.Boolean(), nullable=False)
    )
    op.drop_index("ix_users_email", table_name="users")
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=False)
    op.create_index(op.f("ix_users_role"), "users", ["role"], unique=False)
    op.create_index("user_balance", "users", ["balance"], unique=False)
    op.create_index(
        "user_block_status", "users", ["block_status"], unique=False
    )
    op.create_index("user_email", "users", ["email"], unique=False)
    op.create_index(
        "user_last_activity_at", "users", ["last_activity_at"], unique=False
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index("user_last_activity_at", table_name="users")
    op.drop_index("user_email", table_name="users")
    op.drop_index("user_block_status", table_name="users")
    op.drop_index("user_balance", table_name="users")
    op.drop_index(op.f("ix_users_role"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.drop_column("users", "is_deleted")
    op.drop_column("users", "block_at")
    op.drop_column("users", "block_status")
    op.drop_column("users", "balance")
    op.drop_column("users", "last_activity_at")
    op.drop_column("users", "updated_at")
    op.drop_column("users", "created_at")
    op.drop_column("users", "role")
    op.drop_column("users", "last_name")
    op.drop_column("users", "first_name")
    # ### end Alembic commands ###