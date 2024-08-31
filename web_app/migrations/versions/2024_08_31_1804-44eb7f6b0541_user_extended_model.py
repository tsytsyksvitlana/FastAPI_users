"""user extended model

Revision ID: 44eb7f6b0541
Revises: e30f6720c2e4
Create Date: 2024-08-31 18:04:20.296661

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "44eb7f6b0541"
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
    op.add_column(
        "users", sa.Column("created_at", sa.DateTime(), nullable=False)
    )
    op.add_column(
        "users", sa.Column("updated_at", sa.DateTime(), nullable=True)
    )
    op.add_column(
        "users", sa.Column("last_activity_at", sa.DateTime(), nullable=False)
    )
    op.add_column("users", sa.Column("balance", sa.Integer(), nullable=False))
    op.add_column(
        "users", sa.Column("block_status", sa.Boolean(), nullable=False)
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("users", "block_status")
    op.drop_column("users", "balance")
    op.drop_column("users", "last_activity_at")
    op.drop_column("users", "updated_at")
    op.drop_column("users", "created_at")
    op.drop_column("users", "last_name")
    op.drop_column("users", "first_name")
    # ### end Alembic commands ###
