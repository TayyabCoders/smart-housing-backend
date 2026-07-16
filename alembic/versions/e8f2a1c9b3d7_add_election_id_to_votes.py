"""Add election_id to votes, switch to per-election CNIC uniqueness

Revision ID: e8f2a1c9b3d7
Revises: 342cbcb3e61c
Create Date: 2026-07-17 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e8f2a1c9b3d7'
down_revision: Union[str, Sequence[str], None] = '342cbcb3e61c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Drop the unique index on voter_nic (was created as a unique index, not a constraint)
    op.drop_index('ix_votes_voter_nic', table_name='votes')

    # 2. Add election_id column as nullable first (so existing rows don't immediately fail)
    op.add_column('votes', sa.Column('election_id', sa.UUID(as_uuid=True), nullable=True))

    # 3. Add the FK constraint separately (inline FK in add_column is not reliable)
    op.create_foreign_key(
        'fk_votes_election_id',
        'votes', 'elections',
        ['election_id'], ['id']
    )

    # 4. Back-fill election_id for any existing rows via the candidate relationship
    op.execute("""
        UPDATE votes v
        SET election_id = c.election_id
        FROM candidates c
        WHERE v.candidate_id = c.id
    """)

    # 5. Now make election_id NOT NULL
    op.alter_column('votes', 'election_id', nullable=False)

    # 6. Re-create a plain (non-unique) index on voter_nic for query performance
    op.create_index('ix_votes_voter_nic', 'votes', ['voter_nic'], unique=False)

    # 7. Add composite unique constraint: one CNIC per election
    op.create_unique_constraint('uq_voter_nic_election', 'votes', ['voter_nic', 'election_id'])


def downgrade() -> None:
    op.drop_constraint('uq_voter_nic_election', 'votes', type_='unique')
    op.drop_index('ix_votes_voter_nic', table_name='votes')
    op.drop_constraint('fk_votes_election_id', 'votes', type_='foreignkey')
    op.drop_column('votes', 'election_id')
    # Restore the original unique index on voter_nic
    op.create_index('ix_votes_voter_nic', 'votes', ['voter_nic'], unique=True)
