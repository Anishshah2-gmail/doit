"""create_sessions_table

Revision ID: 0cdade979fc9
Revises: 85f91b417fe7
Create Date: 2025-11-08 02:16:35.335683

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0cdade979fc9'
down_revision: Union[str, Sequence[str], None] = '85f91b417fe7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'sessions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('session_token', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(255), nullable=True),
    )
    # Create compound index for expiration queries
    op.create_index('idx_session_expires', 'sessions', ['expires_at', 'is_active'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('idx_session_expires', table_name='sessions')
    op.drop_table('sessions')
