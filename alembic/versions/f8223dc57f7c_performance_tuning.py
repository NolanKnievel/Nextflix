"""performance tuning

Revision ID: f8223dc57f7c
Revises: 5d6bddc236a9
Create Date: 2025-06-02 17:46:26.362132

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f8223dc57f7c'
down_revision: Union[str, None] = '5d6bddc236a9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    
    # add index on username in users table

    op.execute (
        """
        CREATE INDEX index_users_username_lower_pattern
        ON users (LOWER(username) varchar_pattern_ops)
        """
        
    )

def downgrade() -> None:
    """Downgrade schema."""

    op.execute(
        """
        DROP INDEX IF EXISTS index_users_username_lower_pattern
        """
    )
