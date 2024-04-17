"""initialize db

Revision ID: 072035503c2d
Revises: 
Create Date: 2024-04-17 09:50:16.412143

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '072035503c2d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "employee",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String),
        sa.Column("current", sa.Boolean)
    )


def downgrade() -> None:
    # op.drop_table("employee")
    pass
