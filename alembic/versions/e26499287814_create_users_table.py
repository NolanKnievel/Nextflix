"""create users table

Revision ID: e26499287814
Revises: 
Create Date: 2025-05-04 15:47:04.467412

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e26499287814'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # users - id, username, date_joined, friends
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('username', sa.String(50), nullable=False, unique=True),
        sa.Column('date_joined', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('friends', sa.ARRAY(sa.Integer), nullable=True),
    )

    # username - must be alphanumeric, 3-20 characters long, and start with a letter
    op.create_check_constraint(
        'ck_username',
        'users',
        "username ~ '^[a-zA-Z][a-zA-Z0-9]{2,19}$'",
        comment='Username must be alphanumeric and start with a letter, 3-20 characters long.'
    )

    # username - must be unique
    op.create_unique_constraint(
        'uq_username',
        'users',
        ['username'],
        comment='Username must be unique.'
    )
    


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('users')
