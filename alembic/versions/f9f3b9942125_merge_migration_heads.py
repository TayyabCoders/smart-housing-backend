"""Merge migration heads

Revision ID: f9f3b9942125
Revises: 9c0daa999833, e8f2a1c9b3d7
Create Date: 2026-07-17 03:26:23.536160

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f9f3b9942125'
down_revision: Union[str, Sequence[str], None] = ('9c0daa999833', 'e8f2a1c9b3d7')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
