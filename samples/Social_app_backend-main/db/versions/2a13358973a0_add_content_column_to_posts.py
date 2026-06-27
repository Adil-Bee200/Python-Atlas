"""add content column to posts

Revision ID: 2a13358973a0
Revises: 358479b25c27
Create Date: 2025-07-16 00:23:14.303408

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2a13358973a0'
down_revision: Union[str, Sequence[str], None] = '358479b25c27'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade() -> None:
    op.drop_column('posts', 'content')
    pass
