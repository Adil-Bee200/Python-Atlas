"""add fkey to posts table

Revision ID: 460b45924d7d
Revises: a4eab57c64a7
Create Date: 2025-07-16 00:54:51.299878

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '460b45924d7d'
down_revision: Union[str, Sequence[str], None] = 'a4eab57c64a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('owner_id', sa.Integer(), nullable=False))
    op.create_foreign_key('posts_users_fk', source_table='posts', referent_table='users',
                          local_cols=['owner_id'], remote_cols=['id'], ondelete="CASCADE")
    pass


def downgrade() -> None:
    op.drop_constraint('posts_users_fk',table_name='posts')
    op.drop_column('posts', 'owner_id')
    pass
