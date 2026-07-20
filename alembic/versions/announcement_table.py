"""add announcement table

Revision ID: announcement_table
Revises: f9f3b9942125
Create Date: 2026-07-21 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'announcement_table'
down_revision: Union[str, Sequence[str], None] = 'f9f3b9942125'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE TABLE IF NOT EXISTS announcements (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            created_by UUID NOT NULL,
            title VARCHAR(255) NOT NULL,
            summary VARCHAR(500) NOT NULL,
            description TEXT NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)

    op.execute("CREATE INDEX IF NOT EXISTS ix_announcements_created_by ON announcements (created_by);")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_announcements_created_by'), table_name='announcements')
    op.drop_table('announcements')
