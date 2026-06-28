"""fix complaint status enum to use underscores

Revision ID: fix_complaint_status_enum
Revises: add_user_id_to_complaints
Create Date: 2026-06-28 19:01:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fix_complaint_status_enum'
down_revision: Union[str, None] = 'add_user_id_to_complaints'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Recreate the enum type without spaces first
    op.execute("""
        DO $$
        BEGIN
            -- Drop default constraint first
            ALTER TABLE complaints ALTER COLUMN status DROP DEFAULT;
            
            -- Create new type with underscores
            CREATE TYPE complaint_status_new AS ENUM ('Pending', 'In_Progress', 'Resolved', 'Rejected');
            
            -- Update the column to use new type (this will convert "In Progress" to "In_Progress")
            ALTER TABLE complaints ALTER COLUMN status TYPE complaint_status_new USING 
                CASE 
                    WHEN status::text = 'In Progress' THEN 'In_Progress'::complaint_status_new
                    ELSE status::text::complaint_status_new
                END;
            
            -- Add back default with new type
            ALTER TABLE complaints ALTER COLUMN status SET DEFAULT 'Pending'::complaint_status_new;
            
            -- Drop old type
            DROP TYPE complaint_status;
            
            -- Rename new type to old name
            ALTER TYPE complaint_status_new RENAME TO complaint_status;
        END $$;
    """)


def downgrade() -> None:
    # Revert the changes
    op.execute("""
        DO $$
        BEGIN
            -- Create type with spaces
            CREATE TYPE complaint_status_new AS ENUM ('Pending', 'In Progress', 'Resolved', 'Rejected');
            
            -- Update data back to spaces
            ALTER TABLE complaints ALTER COLUMN status TYPE complaint_status_new USING status::text::complaint_status_new;
            
            -- Drop old type
            DROP TYPE complaint_status;
            
            -- Rename
            ALTER TYPE complaint_status_new RENAME TO complaint_status;
        END $$;
    """)
    
    # Update data back to spaces
    op.execute("UPDATE complaints SET status = 'In Progress' WHERE status = 'In_Progress'")
