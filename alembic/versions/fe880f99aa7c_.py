"""empty message

Revision ID: fe880f99aa7c
Revises: 253133fdc11c
Create Date: 2024-04-26 10:02:39.009948

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fe880f99aa7c'
down_revision: Union[str, None] = '253133fdc11c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('statistic', 'total_duels',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('statistic', 'total_duels',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###
